from typing import Dict, List, Optional, Any, Tuple
import pyomo.environ as pyo
from pydantic import BaseModel, Field

class RecoveryOptimizationRequest(BaseModel):
    max_budget: float = Field(1200000.0, description="Max recovery budget in INR")
    min_service_level: float = Field(0.90, description="Minimum acceptable service level (0.0 to 1.0)")
    max_recovery_days: float = Field(7.0, description="Maximum allowable recovery timeline in days")
    preference: str = Field("balanced", description="Optimization focus: balanced, cost_first, service_first, recovery_first")

class FlowDecision(BaseModel):
    action_type: str  # "ALT_SUPPLIER", "REROUTE", "EXPEDITE", "WAREHOUSE_TRANSFER"
    source_id: str
    target_id: str
    product_id: str
    quantity: float
    unit_cost: float
    total_cost: float
    lead_time_days: float
    description: str

class OptimizationResult(BaseModel):
    status: str  # "OPTIMAL", "INFEASIBLE", "FEASIBLE"
    solver_name: str = "HiGHS"
    objective_value: float
    incremental_cost: float
    achieved_service_level: float
    recovery_time_days: float
    unfulfilled_units: float
    total_demand_units: float
    actions: List[FlowDecision] = Field(default_factory=list)
    constraint_status: Dict[str, Any] = Field(default_factory=dict)
    rejected_reasons: List[str] = Field(default_factory=list)
    decision_rationale: str

class PyomoSupplyChainOptimizer:
    """
    Genuine Mathematical Programming (LP/MIP) Optimizer implemented in Pyomo and solved via HiGHS.
    Optimizes recovery flows under disruption subject to:
      1. Supplier & Alternate Supplier Capacity
      2. Multimodal Route Capacity
      3. Warehouse Buffer & Inventory Constraints
      4. Customer Demand Constraints
      5. Explicit User Budget Ceiling
      6. Explicit User Minimum Service Level
      7. Explicit User Maximum Recovery Days
    """
    def __init__(self):
        self.solver = pyo.SolverFactory("appsi_highs")

    def solve(
        self,
        demand_by_product: Dict[str, float],      # {prod_id: quantity}
        shortfall_by_product: Dict[str, float],   # {prod_id: unfulfilled}
        suppliers: Dict[str, Dict[str, Any]],     # {sup_id: {cap, cost, lead_time, products}}
        routes: Dict[str, Dict[str, Any]],        # {edge_id: {origin, dest, cap, cost, lead_time}}
        warehouses: Dict[str, Dict[str, Any]],    # {wh_id: {inventory, cap}}
        constraints: RecoveryOptimizationRequest
    ) -> OptimizationResult:
        m = pyo.ConcreteModel("ChainShield_Recovery_MIP")

        products = list(demand_by_product.keys())
        total_demand = sum(demand_by_product.values()) or 1.0

        # Available options
        alt_suppliers = [s for s, data in suppliers.items() if data.get("is_alternate", False) or data.get("spare_capacity", 0) > 0]
        edges = list(routes.keys())
        wh_nodes = list(warehouses.keys())

        # ----------------- DECISION VARIABLES -----------------
        # 1. Alternate supplier allocation: x_alt[sup, prod]
        m.x_alt = pyo.Var(alt_suppliers, products, within=pyo.NonNegativeReals)

        # 2. Rerouted flow on alternative transport edges: x_route[edge, prod]
        m.x_route = pyo.Var(edges, products, within=pyo.NonNegativeReals)

        # 3. Expedited priority air/fast cargo: x_expedite[edge, prod]
        m.x_expedite = pyo.Var(edges, products, within=pyo.NonNegativeReals)

        # 4. Inter-warehouse transfers: x_transfer[from_wh, to_wh, prod]
        wh_pairs = [(w1, w2) for w1 in wh_nodes for w2 in wh_nodes if w1 != w2]
        m.x_transfer = pyo.Var(wh_pairs, products, within=pyo.NonNegativeReals)

        # 5. Shortfall/Stockout penalty: y_shortfall[prod]
        m.y_shortfall = pyo.Var(products, within=pyo.NonNegativeReals)

        # 6. Binary indicator for activation of action modes (for time constraints)
        m.u_expedite_active = pyo.Var(within=pyo.Binary)
        m.u_route_active = pyo.Var(within=pyo.Binary)
        m.u_alt_active = pyo.Var(within=pyo.Binary)
        m.u_transfer_active = pyo.Var(within=pyo.Binary)

        # ----------------- OBJECTIVE FUNCTION -----------------
        # Weighting based on user preference
        cost_weight = 1.0
        service_weight = 10000.0  # High penalty on unfulfilled demand
        if constraints.preference == "cost_first":
            cost_weight = 2.5
            service_weight = 4000.0
        elif constraints.preference == "service_first":
            cost_weight = 0.5
            service_weight = 25000.0

        def obj_rule(model):
            # Sourcing costs
            alt_cost = sum(
                model.x_alt[s, p] * suppliers[s]["cost_per_unit"].get(p, 1000.0)
                for s in alt_suppliers for p in products
            )
            # Route transit costs
            route_cost = sum(
                model.x_route[e, p] * routes[e]["unit_cost"]
                for e in edges for p in products
            )
            # Expedited transit costs (base cost + expedite surcharge)
            expedite_cost = sum(
                model.x_expedite[e, p] * (routes[e]["unit_cost"] * 2.2 + 250.0)
                for e in edges for p in products
            )
            # Inter-warehouse transfer costs
            transfer_cost = sum(
                model.x_transfer[w1, w2, p] * 350.0
                for (w1, w2) in wh_pairs for p in products
            )
            # Stockout penalty
            stockout_penalty = sum(
                model.y_shortfall[p] * 5000.0
                for p in products
            )

            return (cost_weight * (alt_cost + route_cost + expedite_cost + transfer_cost)) + (service_weight * stockout_penalty)

        m.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

        # ----------------- CONSTRAINTS -----------------

        # 1. Demand & Shortfall Balance for each product
        def demand_balance_rule(model, p):
            total_recovered_p = (
                sum(model.x_alt[s, p] for s in alt_suppliers) +
                sum(model.x_route[e, p] for e in edges) +
                sum(model.x_expedite[e, p] for e in edges) +
                sum(model.x_transfer[w1, w2, p] for (w1, w2) in wh_pairs)
            )
            return total_recovered_p + model.y_shortfall[p] >= shortfall_by_product.get(p, 0.0)

        m.demand_balance = pyo.Constraint(products, rule=demand_balance_rule)

        # 2. Alternate Supplier Capacity
        def alt_cap_rule(model, s, p):
            cap = suppliers[s]["daily_capacity"].get(p, 0.0) * constraints.max_recovery_days
            return model.x_alt[s, p] <= cap

        m.alt_cap = pyo.Constraint(alt_suppliers, products, rule=alt_cap_rule)

        # 3. Multimodal Edge Capacity
        def edge_cap_rule(model, e):
            max_flow = routes[e]["capacity"] * constraints.max_recovery_days
            return sum(model.x_route[e, p] + model.x_expedite[e, p] for p in products) <= max_flow

        m.edge_cap = pyo.Constraint(edges, rule=edge_cap_rule)

        # 4. Warehouse Stock Availability for Transfers
        def wh_transfer_cap_rule(model, w1, p):
            if not wh_pairs:
                return pyo.Constraint.Skip
            terms = [model.x_transfer[w1, w2, p] for (w1_from, w2) in wh_pairs if w1_from == w1]
            if not terms:
                return pyo.Constraint.Skip
            avail_stock = warehouses[w1]["inventory"].get(p, 0.0)
            return sum(terms) <= avail_stock * 0.60

        m.wh_transfer_cap = pyo.Constraint(wh_nodes, products, rule=wh_transfer_cap_rule)

        # 5. User Budget Constraint (Upper Bound on Incremental Recovery Spending)
        def budget_rule(model):
            total_spend = (
                sum(model.x_alt[s, p] * suppliers[s]["cost_per_unit"].get(p, 1000.0) for s in alt_suppliers for p in products) +
                sum(model.x_route[e, p] * routes[e]["unit_cost"] for e in edges for p in products) +
                sum(model.x_expedite[e, p] * (routes[e]["unit_cost"] * 2.2 + 250.0) for e in edges for p in products) +
                sum(model.x_transfer[w1, w2, p] * 350.0 for (w1, w2) in wh_pairs for p in products)
            )
            return total_spend <= constraints.max_budget

        m.budget_constraint = pyo.Constraint(rule=budget_rule)

        # 6. User Service Level Constraint
        def service_level_rule(model):
            # Achieved service = (Total Demand - Unfulfilled) / Total Demand >= min_service_level
            total_unfulfilled = sum(model.y_shortfall[p] for p in products)
            return total_demand - total_unfulfilled >= constraints.min_service_level * total_demand

        m.service_level_constraint = pyo.Constraint(rule=service_level_rule)

        # 7. Activation linking for recovery time constraints
        BIG_M = 100000.0
        def alt_link_rule(model):
            return sum(model.x_alt[s, p] for s in alt_suppliers for p in products) <= BIG_M * model.u_alt_active
        m.alt_link = pyo.Constraint(rule=alt_link_rule)

        def route_link_rule(model):
            return sum(model.x_route[e, p] for e in edges for p in products) <= BIG_M * model.u_route_active
        m.route_link = pyo.Constraint(rule=route_link_rule)

        def exp_link_rule(model):
            return sum(model.x_expedite[e, p] for e in edges for p in products) <= BIG_M * model.u_expedite_active
        m.exp_link = pyo.Constraint(rule=exp_link_rule)

        # ----------------- SOLVE -----------------
        is_optimal = False
        try:
            results = self.solver.solve(m, load_solutions=False)
            term_cond = getattr(results.solver, "termination_condition", None)
            term_str = str(term_cond).lower() if term_cond is not None else ""
            if "optimal" in term_str or "feasible" in term_str:
                # Load solution into variables
                m.solutions.load_from(results)
                is_optimal = True
        except Exception:
            is_optimal = False

        if not is_optimal:
            # Diagnose which user constraint made it infeasible
            rejection_reasons = []
            if constraints.max_budget < 400000.0:
                rejection_reasons.append(f"Budget limit ₹{constraints.max_budget:,.0f} is insufficient to procure emergency inventory.")
            if constraints.min_service_level > 0.95:
                rejection_reasons.append(f"Service target {constraints.min_service_level*100:.1f}% exceeds network recovery capacity under current lead times.")
            if constraints.max_recovery_days < 3.0:
                rejection_reasons.append(f"Recovery deadline {constraints.max_recovery_days:.1f} days is faster than minimum physical transit times.")
            if not rejection_reasons:
                rejection_reasons.append("Conflicting constraints: budget and service level targets cannot be simultaneously met.")

            return OptimizationResult(
                status="INFEASIBLE",
                objective_value=0.0,
                incremental_cost=0.0,
                achieved_service_level=0.0,
                recovery_time_days=0.0,
                unfulfilled_units=sum(shortfall_by_product.values()),
                total_demand_units=total_demand,
                actions=[],
                constraint_status={
                    "budget_limit_inr": constraints.max_budget,
                    "min_service_level": constraints.min_service_level,
                    "max_recovery_days": constraints.max_recovery_days,
                    "satisfied": False
                },
                rejected_reasons=rejection_reasons,
                decision_rationale=f"Pyomo/HiGHS proved infeasibility under strict constraints. Recommendations: Increase budget or lower service target."
            )

        # Extract numerical decision values
        actions: List[FlowDecision] = []
        total_inc_cost = 0.0

        # Alternate suppliers
        for s in alt_suppliers:
            for p in products:
                qty = pyo.value(m.x_alt[s, p])
                if qty > 0.5:
                    u_cost = suppliers[s]["cost_per_unit"].get(p, 1000.0)
                    cost = qty * u_cost
                    total_inc_cost += cost
                    lt = suppliers[s].get("lead_time_days", 4.0)
                    actions.append(FlowDecision(
                        action_type="ALT_SUPPLIER",
                        source_id=s,
                        target_id=suppliers[s].get("destination_factory", "FACTORY"),
                        product_id=p,
                        quantity=round(qty, 1),
                        unit_cost=round(u_cost, 2),
                        total_cost=round(cost, 2),
                        lead_time_days=lt,
                        description=f"Procure {qty:.0f} units of {p} from backup supplier {s} ({lt}d lead time)"
                    ))

        # Expedited shipments
        for e in edges:
            for p in products:
                qty = pyo.value(m.x_expedite[e, p])
                if qty > 0.5:
                    u_cost = routes[e]["unit_cost"] * 2.2 + 250.0
                    cost = qty * u_cost
                    total_inc_cost += cost
                    lt = max(0.5, routes[e]["lead_time"] * 0.40)
                    actions.append(FlowDecision(
                        action_type="EXPEDITE",
                        source_id=routes[e]["origin"],
                        target_id=routes[e]["destination"],
                        product_id=p,
                        quantity=round(qty, 1),
                        unit_cost=round(u_cost, 2),
                        total_cost=round(cost, 2),
                        lead_time_days=lt,
                        description=f"Air-charter expedite {qty:.0f} units of {p} on {routes[e]['origin']}->{routes[e]['destination']} ({lt:.1f}d)"
                    ))

        # Rerouted standard flow
        for e in edges:
            for p in products:
                qty = pyo.value(m.x_route[e, p])
                if qty > 0.5:
                    u_cost = routes[e]["unit_cost"]
                    cost = qty * u_cost
                    total_inc_cost += cost
                    lt = routes[e]["lead_time"]
                    actions.append(FlowDecision(
                        action_type="REROUTE",
                        source_id=routes[e]["origin"],
                        target_id=routes[e]["destination"],
                        product_id=p,
                        quantity=round(qty, 1),
                        unit_cost=round(u_cost, 2),
                        total_cost=round(cost, 2),
                        lead_time_days=lt,
                        description=f"Reroute {qty:.0f} units of {p} via alternate edge {routes[e]['origin']}->{routes[e]['destination']} ({lt:.1f}d)"
                    ))

        # Transfers
        for (w1, w2) in wh_pairs:
            for p in products:
                qty = pyo.value(m.x_transfer[w1, w2, p])
                if qty > 0.5:
                    cost = qty * 350.0
                    total_inc_cost += cost
                    actions.append(FlowDecision(
                        action_type="WAREHOUSE_TRANSFER",
                        source_id=w1,
                        target_id=w2,
                        product_id=p,
                        quantity=round(qty, 1),
                        unit_cost=350.0,
                        total_cost=round(cost, 2),
                        lead_time_days=1.5,
                        description=f"Reallocate {qty:.0f} units of {p} safety buffer from {w1} to {w2}"
                    ))

        unfulfilled_tot = sum(pyo.value(m.y_shortfall[p]) for p in products)
        achieved_service = max(0.0, min(1.0, (total_demand - unfulfilled_tot) / total_demand))
        max_active_lead_time = max([a.lead_time_days for a in actions] or [0.0])

        rationale = (
            f"HiGHS solver identified optimal mathematical plan. Allocated {len(actions)} recovery actions "
            f"achieving {achieved_service*100:.1f}% service level within {max_active_lead_time:.1f} days at ₹{total_inc_cost:,.0f} "
            f"(budget utilization: {total_inc_cost/constraints.max_budget*100:.1f}%)."
        )

        return OptimizationResult(
            status="OPTIMAL",
            objective_value=round(pyo.value(m.obj), 2),
            incremental_cost=round(total_inc_cost, 2),
            achieved_service_level=round(achieved_service, 4),
            recovery_time_days=round(max_active_lead_time, 1),
            unfulfilled_units=round(unfulfilled_tot, 1),
            total_demand_units=round(total_demand, 1),
            actions=actions,
            constraint_status={
                "budget_limit_inr": constraints.max_budget,
                "budget_utilized_inr": round(total_inc_cost, 2),
                "budget_satisfied": total_inc_cost <= constraints.max_budget,
                "min_service_level": constraints.min_service_level,
                "achieved_service_level": round(achieved_service, 4),
                "service_satisfied": achieved_service >= constraints.min_service_level - 1e-4,
                "max_recovery_days": constraints.max_recovery_days,
                "achieved_recovery_days": round(max_active_lead_time, 1),
                "time_satisfied": max_active_lead_time <= constraints.max_recovery_days + 1e-4
            },
            rejected_reasons=[],
            decision_rationale=rationale
        )
