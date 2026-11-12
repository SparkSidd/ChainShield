from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from data.generator import create_baseline_network
from engine.demand.generator import DemandGenerator, DemandSurge
from engine.simulation.environment import SupplyChainSimulator
from resilience.disruptions.disruption import Disruption, DisruptionType
from resilience.metrics.calculator import MetricsReport

class WhatIfRequest(BaseModel):
    scenario_name: str = "Custom What-If Scenario"
    demand_multiplier: float = Field(1.0, ge=0.2, le=3.0, description="1.0 = normal, 1.3 = +30% surge")
    port_capacity_multiplier: float = Field(1.0, ge=0.0, le=1.0, description="1.0 = 100% capacity, 0.2 = 80% loss")
    supplier_reliability: float = Field(0.98, ge=0.5, le=1.0)
    disruption_duration_days: float = Field(7.0, ge=0.0, le=30.0)
    transport_cost_multiplier: float = Field(1.0, ge=0.5, le=3.0)
    inventory_buffer_multiplier: float = Field(1.0, ge=0.2, le=3.0)
    target_node_id: Optional[str] = "PORT_JNPT"
    recovery_budget_inr: float = 1200000.0
    min_service_level: float = 0.90
    horizon_days: int = 30
    seed: int = 42

class MetricsComparison(BaseModel):
    baseline_value: float
    whatif_value: float
    absolute_delta: float
    percentage_change: float

class WhatIfComparisonResponse(BaseModel):
    scenario_name: str
    seed: int
    baseline_metrics: MetricsReport
    whatif_metrics: MetricsReport
    comparisons: Dict[str, MetricsComparison]
    executive_insight: str
    cascade_summary: Dict[str, Any]

class WhatIfEngine:
    """
    Evaluates dynamic What-If scenarios without mutating the baseline network state.
    Provides reproducible counterfactual sensitivity comparisons.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed

    def run_scenario(self, request: WhatIfRequest) -> WhatIfComparisonResponse:
        seed = request.seed or self.seed

        # 1. Run Baseline (Pure normal operation)
        base_net = create_baseline_network(seed=seed)
        demand_gen = DemandGenerator(seed=seed)
        cust_profiles = {c_id: c.demand_profiles for c_id, c in base_net.get_customers().items()}
        base_schedule = demand_gen.generate_schedule(customer_profiles=cust_profiles, horizon_days=request.horizon_days)

        base_sim = SupplyChainSimulator(network=base_net, horizon_days=request.horizon_days, seed=seed)
        baseline_report, _ = base_sim.run(demand_schedule=base_schedule)

        # 2. Run What-If Scenario with Overrides on fresh network
        whatif_net = create_baseline_network(seed=seed)

        # Apply inventory buffer multiplier to initial inventories
        if request.inventory_buffer_multiplier != 1.0:
            for fac in whatif_net.get_factories().values():
                for k in fac.inventory:
                    fac.inventory[k] *= request.inventory_buffer_multiplier
            for wh in whatif_net.get_warehouses().values():
                for k in wh.inventory:
                    wh.inventory[k] *= request.inventory_buffer_multiplier

        # Apply transport cost multiplier
        if request.transport_cost_multiplier != 1.0:
            for edge in whatif_net.edges.values():
                edge.cost_per_unit_km *= request.transport_cost_multiplier

        # Apply supplier reliability
        for sup in whatif_net.get_suppliers().values():
            sup.reliability = request.supplier_reliability

        # Build modified demand schedule
        whatif_schedule = {}
        for d, custs in base_schedule.items():
            whatif_schedule[d] = {}
            for cid, prods in custs.items():
                whatif_schedule[d][cid] = {
                    p: round(qty * request.demand_multiplier, 1)
                    for p, qty in prods.items()
                }

        whatif_sim = SupplyChainSimulator(network=whatif_net, horizon_days=request.horizon_days, seed=seed)

        # Apply port or target disruption if specified
        if request.port_capacity_multiplier < 1.0 or request.disruption_duration_days > 0:
            target_id = request.target_node_id or "PORT_JNPT"
            whatif_sim.add_disruption(Disruption(
                id="WHATIF_DISR",
                name=f"What-If Disruption: {target_id}",
                disruption_type=DisruptionType.PORT_STRIKE if "PORT" in target_id else DisruptionType.VEHICLE_BREAKDOWN,
                target_id=target_id,
                start_day=4.0,
                duration_days=request.disruption_duration_days,
                capacity_multiplier=request.port_capacity_multiplier,
                delay_multiplier=round(1.0 + (1.0 - request.port_capacity_multiplier) * 2.0, 2)
            ))

        whatif_report, whatif_telemetry = whatif_sim.run(demand_schedule=whatif_schedule)

        # 3. Compute structured comparisons
        def comp(base_val: float, whatif_val: float) -> MetricsComparison:
            delta = whatif_val - base_val
            pct = (delta / (base_val or 1e-6)) * 100.0
            return MetricsComparison(
                baseline_value=round(base_val, 2),
                whatif_value=round(whatif_val, 2),
                absolute_delta=round(delta, 2),
                percentage_change=round(pct, 1)
            )

        comparisons = {
            "service_level": comp(baseline_report.service_level, whatif_report.service_level),
            "otif_rate": comp(baseline_report.otif_rate, whatif_report.otif_rate),
            "total_cost_inr": comp(
                baseline_report.total_transport_cost + baseline_report.total_holding_cost + baseline_report.total_financial_loss,
                whatif_report.total_transport_cost + whatif_report.total_holding_cost + whatif_report.total_financial_loss
            ),
            "unfulfilled_units": comp(baseline_report.unfulfilled_demand_units, whatif_report.unfulfilled_demand_units),
            "resilience_score": comp(baseline_report.resilience_score, whatif_report.resilience_score),
            "avg_delay_days": comp(baseline_report.avg_shipment_delay_days, whatif_report.avg_shipment_delay_days)
        }

        # Executive insight
        s_delta = comparisons["service_level"].absolute_delta
        c_pct = comparisons["total_cost_inr"].percentage_change
        insight = (
            f"Under scenario '{request.scenario_name}' (Demand: {request.demand_multiplier:.1f}x, "
            f"Port Capacity: {int(request.port_capacity_multiplier*100)}% for {request.disruption_duration_days:.0f}d): "
            f"Customer service level changes by {s_delta*100:+.1f}% (from {baseline_report.service_level*100:.1f}% to {whatif_report.service_level*100:.1f}%), "
            f"while operating cost changes by {c_pct:+.1f}%. Resilience score stands at {whatif_report.resilience_score:.1f}/100."
        )

        return WhatIfComparisonResponse(
            scenario_name=request.scenario_name,
            seed=seed,
            baseline_metrics=baseline_report,
            whatif_metrics=whatif_report,
            comparisons=comparisons,
            executive_insight=insight,
            cascade_summary=whatif_telemetry.get("cascade", {})
        )
