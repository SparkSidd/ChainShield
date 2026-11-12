import pytest
from data.generator import create_baseline_network
from engine.demand.generator import DemandGenerator, DemandSurge
from engine.simulation.environment import SupplyChainSimulator
from resilience.disruptions.disruption import Disruption, DisruptionType
from optimization.recovery_engine import ConstraintDrivenOptimizer, RecoveryStrategyType

def test_baseline_network_topology():
    net = create_baseline_network(seed=42)
    assert len(net.nodes) == 29  # 8 suppliers + 2 ports + 3 factories + 4 warehouses + 12 customers = 29
    assert len(net.get_suppliers()) == 8
    assert len(net.get_ports()) == 2
    assert len(net.get_factories()) == 3
    assert len(net.get_warehouses()) == 4
    assert len(net.get_customers()) == 12
    assert len(net.products) == 6
    assert len(net.edges) >= 25

    # Check connectivity: customer path to a factory exists
    path = net.find_shortest_path("WH_MUMBAI", "CUST_MUMBAI")
    assert path is not None
    assert path == ["WH_MUMBAI", "CUST_MUMBAI"]

def test_baseline_30_day_simulation_healthy():
    net = create_baseline_network(seed=42)
    demand_gen = DemandGenerator(seed=42)

    # Collect customer profiles
    profiles = {c_id: c.demand_profiles for c_id, c in net.get_customers().items()}
    schedule = demand_gen.generate_schedule(customer_profiles=profiles, horizon_days=30)

    sim = SupplyChainSimulator(network=net, horizon_days=30, seed=42)
    report, telemetry = sim.run(demand_schedule=schedule)

    assert report.service_level >= 0.90
    assert report.total_demand_units > 0
    assert report.fulfilled_demand_units > 0
    assert report.resilience_score > 70.0
    assert len(telemetry["daily_timeseries"]) == 30
    assert len(sim.events) > 50

def test_port_strike_disruption_and_cascade_trace():
    net = create_baseline_network(seed=42)
    demand_gen = DemandGenerator(seed=42)
    profiles = {c_id: c.demand_profiles for c_id, c in net.get_customers().items()}
    schedule = demand_gen.generate_schedule(customer_profiles=profiles, horizon_days=30)

    sim = SupplyChainSimulator(network=net, horizon_days=30, seed=42)

    # Inject major Port Strike at JNPT Mumbai (Day 5 to Day 15, capacity choked by 80%)
    port_strike = Disruption(
        id="DISR_PORT_STRIKE_JNPT",
        name="JNPT Terminal Dockworkers Strike",
        disruption_type=DisruptionType.PORT_STRIKE,
        target_id="PORT_JNPT",
        start_day=5.0,
        duration_days=10.0,
        capacity_multiplier=0.20,
        delay_multiplier=2.5,
        description="Container backlog at JNPT halts 80% of incoming chip cargo"
    )
    sim.add_disruption(port_strike)

    report, telemetry = sim.run(demand_schedule=schedule)

    # Port strike must degrade service or create delays
    assert report.delayed_shipments > 0 or report.unfulfilled_demand_units > 0
    assert len(telemetry["cascade"]["chain"]) > 0

    # Verify cascade recorded upstream to downstream transitions
    cascade_chain = telemetry["cascade"]["chain"]
    impacted_nodes = [l["target_node"] for l in cascade_chain]
    assert "PORT_JNPT" in impacted_nodes

def test_constraint_driven_recovery_optimizer():
    optimizer = ConstraintDrivenOptimizer(
        max_additional_cost=1200000.0,  # ₹12 Lakhs
        min_service_level=0.90,         # 90%
        max_recovery_days=7.0           # 7 days
    )

    candidates = optimizer.generate_candidate_strategies(
        disrupted_target_id="PORT_JNPT",
        unfulfilled_demand_units=500.0,
        daily_loss_inr=150000.0
    )

    result = optimizer.optimize_recovery(candidates, preference="balanced")
    assert result["status"] == "OPTIMAL"
    assert result["recommended_strategy"] is not None
    # Alternate supplier costs ₹8.5L (< ₹12L) and recovers in 5 days (<= 7 days) with 92.5% service (>= 90%)
    assert result["recommended_strategy"]["strategy_id"] in ["REC_ALT_SUPPLIER", "REC_WH_REALLOCATION"]

    # Infeasible test: if budget is set too low (e.g. ₹3 Lakhs), no strategy can satisfy all constraints
    tight_optimizer = ConstraintDrivenOptimizer(max_additional_cost=300000.0, min_service_level=0.95, max_recovery_days=3.0)
    tight_candidates = tight_optimizer.generate_candidate_strategies("PORT_JNPT", 500.0, 150000.0)
    tight_result = tight_optimizer.optimize_recovery(tight_candidates)
    assert tight_result["status"] == "INFEASIBLE"
    assert "No candidate recovery strategy satisfies all constraints" in tight_result["explanation"]
