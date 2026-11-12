from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from optimization.recovery_engine import EvaluatedStrategy, RecoveryStrategyType
from optimization.mip_solver import PyomoSupplyChainOptimizer, RecoveryOptimizationRequest, OptimizationResult

class ParetoPoint(BaseModel):
    strategy_id: str
    name: str
    cost_inr: float
    recovery_days: float
    service_level: float
    is_pareto_optimal: bool

class RecoveryArenaComparison(BaseModel):
    baseline_disrupted_service: float
    baseline_disrupted_loss_inr: float
    unfulfilled_demand_units: float
    strategies: List[EvaluatedStrategy]
    pareto_frontier: List[ParetoPoint]
    user_constraints: Dict[str, Any]
    best_feasible_strategy: Optional[EvaluatedStrategy] = None
    mathematical_mip_plan: Optional[OptimizationResult] = None
    executive_recommendation: str

class RecoveryArenaService:
    """
    Evaluates candidate recovery options side-by-side for the exact same disruption state.
    Calculates the true multi-dimensional Pareto frontier (Cost vs. Recovery Time vs. Service Level)
    and validates feasibility against user-defined budget and operational deadlines.
    """
    def __init__(self):
        self.mip_optimizer = PyomoSupplyChainOptimizer()

    def compare_strategies(
        self,
        disrupted_target_id: str,
        unfulfilled_demand_units: float,
        disrupted_service_level: float,
        daily_loss_inr: float,
        max_budget: float = 1200000.0,
        min_service_level: float = 0.90,
        max_recovery_days: float = 7.0,
        preference: str = "balanced",
        suppliers_data: Optional[Dict[str, Any]] = None,
        routes_data: Optional[Dict[str, Any]] = None,
        warehouses_data: Optional[Dict[str, Any]] = None
    ) -> RecoveryArenaComparison:
        # 1. Define candidate strategies
        strategies = [
            EvaluatedStrategy(
                strategy_id="REC_ALT_SUPPLIER",
                name="Activate Domestic Backup Supplier (ISL Bengaluru & Bhilai Alloys)",
                strategy_type=RecoveryStrategyType.ALTERNATE_SUPPLIER,
                description="Shift 60% of component procurement to domestic Tier-1 suppliers, bypassing maritime port choke.",
                incremental_cost_inr=850000.0,      # ₹8.5 Lakhs
                expected_recovery_days=5.0,         # 5 days
                expected_service_level=0.925,       # 92.5%
                stockout_reduction_units=round(unfulfilled_demand_units * 0.82, 0),
                resilience_gain_pct=18.5
            ),
            EvaluatedStrategy(
                strategy_id="REC_REROUTE_RAIL",
                name="Multimodal Reroute via Chennai Port Rail Corridor",
                strategy_type=RecoveryStrategyType.REROUTE,
                description="Divert delayed containers through southern rail corridor directly to Pune and Manesar assembly plants.",
                incremental_cost_inr=680000.0,      # ₹6.8 Lakhs
                expected_recovery_days=8.5,         # 8.5 days (fails 7d max constraint)
                expected_service_level=0.880,       # 88.0% (fails 90% service constraint)
                stockout_reduction_units=round(unfulfilled_demand_units * 0.65, 0),
                resilience_gain_pct=12.0
            ),
            EvaluatedStrategy(
                strategy_id="REC_EXPEDITE_AIR",
                name="Emergency Expedited Air Freight",
                strategy_type=RecoveryStrategyType.EXPEDITED_TRANSPORT,
                description="Charter dedicated priority air cargo for microcontrollers directly to Pune plant within 48 hours.",
                incremental_cost_inr=1850000.0,     # ₹18.5 Lakhs (fails budget constraint)
                expected_recovery_days=2.5,         # 2.5 days (fastest)
                expected_service_level=0.965,       # 96.5% (highest service)
                stockout_reduction_units=round(unfulfilled_demand_units * 0.95, 0),
                resilience_gain_pct=24.0
            ),
            EvaluatedStrategy(
                strategy_id="REC_WH_REALLOCATION",
                name="Inter-Warehouse Safety Stock Reallocation",
                strategy_type=RecoveryStrategyType.INVENTORY_REALLOCATION,
                description="Reallocate safety stock from South (Bengaluru) and North (Gurgaon) hubs to cover western shortfall.",
                incremental_cost_inr=420000.0,      # ₹4.2 Lakhs (lowest cost)
                expected_recovery_days=6.0,         # 6 days
                expected_service_level=0.908,       # 90.8%
                stockout_reduction_units=round(unfulfilled_demand_units * 0.72, 0),
                resilience_gain_pct=15.0
            )
        ]

        # 2. Validate feasibility against user constraints
        for s in strategies:
            reasons = []
            if s.incremental_cost_inr > max_budget:
                reasons.append(f"Cost ₹{s.incremental_cost_inr:,.0f} exceeds budget limit ₹{max_budget:,.0f}")
            if s.expected_service_level < min_service_level:
                reasons.append(f"Service level {s.expected_service_level*100:.1f}% below target {min_service_level*100:.1f}%")
            if s.expected_recovery_days > max_recovery_days:
                reasons.append(f"Recovery time {s.expected_recovery_days:.1f}d exceeds max allowance {max_recovery_days:.1f}d")

            if reasons:
                s.feasible = False
                s.infeasibility_reasons = reasons
            else:
                s.feasible = True
                s.infeasibility_reasons = []

        # 3. Calculate Pareto Frontier (dominated if another strategy has lower/equal cost, higher/equal service, AND faster/equal recovery)
        pareto_points: List[ParetoPoint] = []
        for s in strategies:
            dominated = False
            for other in strategies:
                if other.strategy_id == s.strategy_id:
                    continue
                # other is strictly better or equal on all 3 dimensions, and strictly better on at least one
                better_cost = other.incremental_cost_inr <= s.incremental_cost_inr
                better_service = other.expected_service_level >= s.expected_service_level
                better_time = other.expected_recovery_days <= s.expected_recovery_days

                strictly_better = (
                    other.incremental_cost_inr < s.incremental_cost_inr or
                    other.expected_service_level > s.expected_service_level or
                    other.expected_recovery_days < s.expected_recovery_days
                )
                if better_cost and better_service and better_time and strictly_better:
                    dominated = True
                    break

            pareto_points.append(ParetoPoint(
                strategy_id=s.strategy_id,
                name=s.name,
                cost_inr=s.incremental_cost_inr,
                recovery_days=s.expected_recovery_days,
                service_level=s.expected_service_level,
                is_pareto_optimal=not dominated
            ))

        # 4. Select best feasible strategy based on preference
        feasible_strategies = [s for s in strategies if s.feasible]
        best_strategy = None

        if feasible_strategies:
            if preference == "cost_first":
                best_strategy = min(feasible_strategies, key=lambda x: x.incremental_cost_inr)
            elif preference == "service_first":
                best_strategy = max(feasible_strategies, key=lambda x: x.expected_service_level)
            elif preference == "recovery_first":
                best_strategy = min(feasible_strategies, key=lambda x: x.expected_recovery_days)
            else: # balanced
                def score(x):
                    cost_factor = 1.0 - (x.incremental_cost_inr / max(max_budget, 1.0))
                    service_factor = x.expected_service_level
                    time_factor = 1.0 - (x.expected_recovery_days / max(max_recovery_days, 1.0))
                    return (0.35 * cost_factor) + (0.40 * service_factor) + (0.25 * time_factor)
                best_strategy = max(feasible_strategies, key=score)

        # 5. Formulate MIP solver recovery plan if input data supplied
        mip_plan = None
        if suppliers_data and routes_data and warehouses_data:
            req = RecoveryOptimizationRequest(
                max_budget=max_budget,
                min_service_level=min_service_level,
                max_recovery_days=max_recovery_days,
                preference=preference
            )
            mip_plan = self.mip_optimizer.solve(
                demand_by_product={"FG_SMART_IOT": unfulfilled_demand_units * 0.5, "FG_TELECOM_NODE": unfulfilled_demand_units * 0.5},
                shortfall_by_product={"FG_SMART_IOT": unfulfilled_demand_units * 0.5, "FG_TELECOM_NODE": unfulfilled_demand_units * 0.5},
                suppliers=suppliers_data,
                routes=routes_data,
                warehouses=warehouses_data,
                constraints=req
            )

        # Executive summary
        if best_strategy:
            rec_text = (
                f"RECOMMENDED: '{best_strategy.name}' satisfies all operational constraints: "
                f"Budget ₹{best_strategy.incremental_cost_inr:,.0f} (<= ₹{max_budget:,.0f}), "
                f"Service {best_strategy.expected_service_level*100:.1f}% (>= {min_service_level*100:.1f}%), "
                f"Recovery in {best_strategy.expected_recovery_days:.1f} days (<= {max_recovery_days:.1f}d). "
                f"Stockout reduction: {best_strategy.stockout_reduction_units:.0f} units."
            )
        else:
            rec_text = (
                f"INFEASIBLE: No recovery strategy satisfies Budget <= ₹{max_budget:,.0f}, "
                f"Service >= {min_service_level*100:.1f}%, and Recovery <= {max_recovery_days:.1f} days simultaneously. "
                f"Suggested mitigation: Relax recovery budget ceiling to at least ₹8.5L or extend deadline to 8.5 days."
            )

        return RecoveryArenaComparison(
            baseline_disrupted_service=round(disrupted_service_level, 4),
            baseline_disrupted_loss_inr=round(daily_loss_inr, 2),
            unfulfilled_demand_units=round(unfulfilled_demand_units, 1),
            strategies=strategies,
            pareto_frontier=pareto_points,
            user_constraints={
                "max_budget_inr": max_budget,
                "min_service_level": min_service_level,
                "max_recovery_days": max_recovery_days,
                "preference": preference
            },
            best_feasible_strategy=best_strategy,
            mathematical_mip_plan=mip_plan,
            executive_recommendation=rec_text
        )
