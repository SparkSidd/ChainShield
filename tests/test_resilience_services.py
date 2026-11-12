import pytest
from resilience.stress_testing.stress_lab import StressTestEngine
from resilience.criticality.criticality_engine import CriticalityEngine
from engine.whatif.whatif_engine import WhatIfEngine, WhatIfRequest
from engine.redesign.redesign_engine import NetworkRedesignEngine, RedesignConfiguration

def test_stress_test_engine():
    engine = StressTestEngine(seed=42)
    summary, results = engine.run_stress_test(runs=10, horizon_days=15)

    assert summary.total_scenarios_run == 10
    assert len(results) == 10
    assert summary.mean_cost_inr > 0
    assert 0.0 <= summary.mean_service_level <= 1.0
    assert len(summary.loss_distribution_buckets) > 0
    assert len(summary.top_vulnerable_targets) > 0

def test_criticality_engine_rankings():
    crit_engine = CriticalityEngine(seed=42)
    report = crit_engine.run_criticality_analysis()

    assert len(report.most_critical_ports) == 2
    assert report.most_critical_ports[0].id == "PORT_JNPT"  # JNPT is highest volume
    assert report.most_critical_ports[0].criticality_score >= 0.65
    assert report.most_critical_ports[0].criticality_score > report.most_critical_ports[1].criticality_score

    assert len(report.most_critical_suppliers) > 0
    assert len(report.failure_mode_comparison) == 4
    # Targeted failure must show higher loss than random failure
    targeted = next(f for f in report.failure_mode_comparison if f.mode == "TARGETED_CRITICAL_FAILURE")
    random_f = next(f for f in report.failure_mode_comparison if f.mode == "RANDOM_FAILURE")
    assert targeted.service_loss_pct >= random_f.service_loss_pct

def test_whatif_engine_immutability_and_diff():
    engine = WhatIfEngine(seed=42)
    req = WhatIfRequest(
        scenario_name="Port JNPT Strike + Demand Surge",
        demand_multiplier=1.40,          # +40% surge
        port_capacity_multiplier=0.10,   # -90% strike
        inventory_buffer_multiplier=0.30, # Low initial buffers
        disruption_duration_days=12.0,
        horizon_days=25
    )
    res = engine.run_scenario(req)

    # What-if must show elevated delays or degraded service
    assert res.whatif_metrics.delayed_shipments > res.baseline_metrics.delayed_shipments or res.whatif_metrics.service_level <= res.baseline_metrics.service_level
    assert res.comparisons["total_cost_inr"].percentage_change > 0.0
    assert len(res.comparisons) >= 5
    assert len(res.executive_insight) > 20

def test_network_redesign_resilience_gain():
    redesign_engine = NetworkRedesignEngine(seed=42)
    cfg = RedesignConfiguration(
        add_backup_chip_supplier=True,
        add_freight_corridor_bypass=True,
        increase_safety_stock_pct=30.0,
        add_mundra_alternate_port=True
    )
    comparison = redesign_engine.evaluate_redesign_resilience(config=cfg, stress_runs=10)

    assert len(comparison.structural_changes_applied) == 4
    assert len(comparison.criticality_shifts) >= 3
    # JNPT criticality must drop
    jnpt_shift = next(s for s in comparison.criticality_shifts if s["node_id"] == "PORT_JNPT")
    assert jnpt_shift["after_score"] < jnpt_shift["before_score"]
