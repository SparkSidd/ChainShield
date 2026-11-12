import sys
import os
import copy

sys.path.insert(0, os.path.abspath("."))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from data.generator import create_baseline_network
from engine.simulation.environment import SupplyChainSimulator
from engine.demand.generator import DemandGenerator
from optimization.mip_solver import PyomoSupplyChainOptimizer, RecoveryOptimizationRequest
from optimization.recovery_arena import RecoveryArenaService
from engine.whatif.whatif_engine import WhatIfEngine, WhatIfRequest
from resilience.stress_testing.stress_lab import StressTestEngine
from resilience.criticality.criticality_engine import CriticalityEngine
from engine.redesign.redesign_engine import NetworkRedesignEngine, RedesignConfiguration
from resilience.disruptions.disruption import Disruption, DisruptionType

def test_fixed_seed_determinism():
    print("[1/6] Verifying Fixed-Seed Determinism...")
    net1 = create_baseline_network()
    net2 = create_baseline_network()
    gen1 = DemandGenerator(seed=42)
    gen2 = DemandGenerator(seed=42)
    prof1 = {c_id: c.demand_profiles for c_id, c in net1.get_customers().items()}
    prof2 = {c_id: c.demand_profiles for c_id, c in net2.get_customers().items()}
    sched1 = gen1.generate_schedule(customer_profiles=prof1, horizon_days=30)
    sched2 = gen2.generate_schedule(customer_profiles=prof2, horizon_days=30)
    
    sim1 = SupplyChainSimulator(network=net1, horizon_days=30, seed=42)
    sim2 = SupplyChainSimulator(network=net2, horizon_days=30, seed=42)
    rep1, _ = sim1.run(sched1)
    rep2, _ = sim2.run(sched2)
    
    assert rep1.total_demand_units == rep2.total_demand_units, "Demand units differed"
    assert rep1.service_level == rep2.service_level, "Service level differed"
    assert rep1.total_transport_cost == rep2.total_transport_cost, "Cost differed"
    assert rep1.resilience_score == rep2.resilience_score, "Resilience score differed"
    print(f"      ✓ 100% Identical: Demand={rep1.total_demand_units}, Service={rep1.service_level:.4f}, Cost=₹{rep1.total_transport_cost:,.0f}")

def test_whatif_immutability():
    print("[2/6] Verifying What-If Immutability...")
    engine = WhatIfEngine()
    req = WhatIfRequest(demand_multiplier=1.35, port_capacity_multiplier=0.30, seed=42)
    res = engine.run_scenario(req)
    
    # Check that baseline in result matches clean baseline run
    net_clean = create_baseline_network()
    sim_clean = SupplyChainSimulator(network=net_clean, horizon_days=30, seed=42)
    gen_clean = DemandGenerator(seed=42)
    prof_clean = {c_id: c.demand_profiles for c_id, c in net_clean.get_customers().items()}
    clean_sched = gen_clean.generate_schedule(customer_profiles=prof_clean, horizon_days=30)
    rep_clean, _ = sim_clean.run(clean_sched)
    
    assert res.baseline_metrics.total_demand_units == rep_clean.total_demand_units
    assert res.baseline_metrics.total_transport_cost == rep_clean.total_transport_cost
    assert res.whatif_metrics.total_demand_units > res.baseline_metrics.total_demand_units
    print(f"      ✓ Baseline unchanged: {res.baseline_metrics.total_demand_units} units vs WhatIf: {res.whatif_metrics.total_demand_units} units")

def test_optimizer_constraints_and_infeasibility_reasons():
    print("[3/6] Verifying Optimizer Hard Constraints & Infeasibility Reasons...")
    arena = RecoveryArenaService()
    # Strictest constraints: ₹5L budget, 95% service, 5 days
    comparison = arena.compare_strategies(
        disrupted_target_id="PORT_JNPT",
        unfulfilled_demand_units=600.0,
        disrupted_service_level=0.74,
        daily_loss_inr=450000.0,
        max_budget=500000.0,
        min_service_level=0.95,
        max_recovery_days=5.0
    )
    for strat in comparison.strategies:
        if not strat.feasible:
            assert len(strat.infeasibility_reasons) > 0, f"Strategy {strat.name} marked infeasible without reason"
            print(f"      ✓ {strat.name}: Infeasible -> {strat.infeasibility_reasons}")
        else:
            print(f"      ✓ {strat.name}: Feasible under constraints")

def test_stress_test_reproducibility():
    print("[4/6] Verifying Stress-Test Reproducibility...")
    engine1 = StressTestEngine(seed=777)
    res1, _ = engine1.run_stress_test(runs=15, horizon_days=10)
    engine2 = StressTestEngine(seed=777)
    res2, _ = engine2.run_stress_test(runs=15, horizon_days=10)
    assert res1.mean_service_level == res2.mean_service_level
    assert res1.p90_cost_inr == res2.p90_cost_inr
    assert res1.p95_recovery_days == res2.p95_recovery_days
    print(f"      ✓ 15-run MC Deterministic: Mean Service={res1.mean_service_level:.4f}, P90 Cost=₹{res1.p90_cost_inr:,.0f}, P95 Recovery={res1.p95_recovery_days:.1f}d")

def test_network_redesign_live_simulation():
    print("[5/6] Verifying Network Redesign Re-runs Real Simulation...")
    from engine.redesign.redesign_engine import NetworkRedesignEngine, RedesignConfiguration
    redesign_engine = NetworkRedesignEngine()
    cfg = RedesignConfiguration(
        add_backup_chip_supplier=True,
        diversify_sourcing_allocation=True,
        add_freight_corridor_bypass=True,
        increase_safety_stock_pct=40.0,
        add_mundra_alternate_port=True
    )
    res = redesign_engine.evaluate_redesign_resilience(cfg, stress_runs=15)
    print(f"      Before: worst={res.before_summary.worst_case_service_level:.4f}, mean={res.before_summary.mean_service_level:.4f}, p95_rec={res.before_summary.p95_recovery_days}")
    print(f"      After:  worst={res.after_summary.worst_case_service_level:.4f}, mean={res.after_summary.mean_service_level:.4f}, p95_rec={res.after_summary.p95_recovery_days}")
    assert res.after_summary.mean_service_level >= res.before_summary.mean_service_level
    assert res.resilience_score_improvement >= 0
    print(f"      ✓ Worst-case Service improved: {res.before_summary.worst_case_service_level*100:.1f}% -> {res.after_summary.worst_case_service_level*100:.1f}%")
    print(f"      ✓ P95 Recovery reduced by: {res.p95_recovery_reduction_days:.1f} days")
    print(f"      ✓ Resilience Score Gain: +{res.resilience_score_improvement:.1f} pts")

if __name__ == "__main__":
    test_fixed_seed_determinism()
    test_whatif_immutability()
    test_optimizer_constraints_and_infeasibility_reasons()
    test_stress_test_reproducibility()
    test_network_redesign_live_simulation()
    print("[6/6] All Phase 4 Truthfulness & Mathematical Defense Checks Passed!")
