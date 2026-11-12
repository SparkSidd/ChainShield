"""
CHAINSHIELD End-to-End Primary Demo Workflow Validation Script
Executes:
  1. BASELINE: Healthy 30-day supply chain run
  2. PORT STRIKE: 80% capacity knockout at JNPT Mumbai
  3. CASCADE TRACE: Causal shock propagation from port to end-customer
  4. IMPACT QUANTIFICATION: Loss measurement across service, OTIF, and finance
  5. RECOVERY ARENA: Side-by-side trade-off comparison of 4 candidate strategies & Pareto frontier
  6. OPTIMIZATION: Pyomo + HiGHS solver finding optimal feasible allocation under ₹12L budget & 90% service target
  7. WHAT-IF: +30% demand surge scenario evaluated counterfactually against baseline
  8. STRESS TEST: 100-run Monte Carlo stress testing producing risk and loss distributions
  9. NETWORK REDESIGN: Hardening network with Hyderabad foundry, Mundra Port, and rail bypass
"""
import time
import json
import os
import sys
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from data.generator import create_baseline_network
from engine.demand.generator import DemandGenerator
from engine.simulation.environment import SupplyChainSimulator
from resilience.disruptions.disruption import Disruption, DisruptionType
from optimization.recovery_arena import RecoveryArenaService
from optimization.mip_solver import PyomoSupplyChainOptimizer, RecoveryOptimizationRequest
from engine.whatif.whatif_engine import WhatIfEngine, WhatIfRequest
from resilience.stress_testing.stress_lab import StressTestEngine
from engine.redesign.redesign_engine import NetworkRedesignEngine, RedesignConfiguration

def run_e2e_validation():
    print("=" * 80)
    print("CHAINSHIELD — FULL PRIMARY DEMO WORKFLOW VALIDATION")
    print("=" * 80)
    start_total_time = time.time()

    # 1. BASELINE
    print("\n[STEP 1: BASELINE HEALTHY NETWORK]")
    t0 = time.time()
    net = create_baseline_network(seed=42)
    demand_gen = DemandGenerator(seed=42)
    profiles = {c_id: c.demand_profiles for c_id, c in net.get_customers().items()}
    schedule = demand_gen.generate_schedule(customer_profiles=profiles, horizon_days=30)
    sim = SupplyChainSimulator(network=net, horizon_days=30, seed=42)
    base_report, base_telemetry = sim.run(demand_schedule=schedule)
    t_base = time.time() - t0

    print(f"  ✓ Service Level:        {base_report.service_level*100:.1f}%")
    print(f"  ✓ Total Operating Cost: ₹{(base_report.total_transport_cost+base_report.total_holding_cost)/1e5:.1f} Lakhs")
    print(f"  ✓ Stockout Units:       {base_report.unfulfilled_demand_units:.0f} units")
    print(f"  ✓ Delayed Shipments:    {base_report.delayed_shipments}")
    print(f"  ✓ Resilience Score:     {base_report.resilience_score:.1f}/100")
    print(f"  Runtime: {t_base:.2f}s")

    # 2. PORT STRIKE DISRUPTION
    print("\n[STEP 2: PORT STRIKE DISRUPTION AT JNPT MUMBAI]")
    t0 = time.time()
    disrupted_net = create_baseline_network(seed=42)
    sim_disr = SupplyChainSimulator(network=disrupted_net, horizon_days=30, seed=42)
    port_strike = Disruption(
        id="DISR_PORT_STRIKE_JNPT",
        name="JNPT Port Marine Terminal Strike",
        disruption_type=DisruptionType.PORT_STRIKE,
        target_id="PORT_JNPT",
        start_day=5.0,
        duration_days=10.0,
        capacity_multiplier=0.20, # 80% loss
        delay_multiplier=2.5,
        description="Dockworkers strike halts container movement at JNPT"
    )
    sim_disr.add_disruption(port_strike)
    disr_report, disr_telemetry = sim_disr.run(demand_schedule=schedule)
    t_disr = time.time() - t0

    print(f"  ! Disrupted Service:    {disr_report.service_level*100:.1f}% (Drop: {((base_report.service_level - disr_report.service_level)/base_report.service_level)*100:.1f}%)")
    print(f"  ! Delayed Shipments:    {disr_report.delayed_shipments} consignments")
    print(f"  ! Total Financial Loss: ₹{(disr_report.total_financial_loss)/1e5:.1f} Lakhs")
    print(f"  ! Resilience Score:     {disr_report.resilience_score:.1f}/100")
    print(f"  Runtime: {t_disr:.2f}s")

    # 3. CASCADE TRACE
    print("\n[STEP 3: CAUSAL CASCADE TRACE]")
    cascade_chain = disr_telemetry["cascade"]["chain"]
    print(f"  ✓ Recorded {len(cascade_chain)} causal transition links:")
    for idx, link in enumerate(cascade_chain[:5], 1):
        print(f"    {idx}. [Day {link['timestamp']}] {link['source_node_or_edge']} -> {link['target_node']}: {link['effect_type']} ({link['magnitude']}{link['magnitude_unit']})")
        print(f"       Summary: {link['downstream_impact_summary']}")

    # 4. RECOVERY ARENA & PARETO FRONTIER
    print("\n[STEP 4: RECOVERY ARENA & PARETO COMPARISON]")
    t0 = time.time()
    arena = RecoveryArenaService()
    comparison = arena.compare_strategies(
        disrupted_target_id="PORT_JNPT",
        unfulfilled_demand_units=disr_report.unfulfilled_demand_units or 600.0,
        disrupted_service_level=disr_report.service_level,
        daily_loss_inr=disr_report.total_financial_loss,
        max_budget=1200000.0,
        min_service_level=0.90,
        max_recovery_days=7.0,
        preference="balanced"
    )
    t_arena = time.time() - t0
    for s in comparison.strategies:
        status_str = "FEASIBLE" if s.feasible else f"INVALID ({s.infeasibility_reasons[0]})"
        print(f"  • {s.name[:38]:<38} | Cost: ₹{s.incremental_cost_inr/1e5:.1f}L | Rec: {s.expected_recovery_days:.1f}d | Svc: {s.expected_service_level*100:.1f}% | [{status_str}]")
    print(f"  ✓ Recommended Strategy: {comparison.best_feasible_strategy.name if comparison.best_feasible_strategy else 'None'}")
    print(f"  Runtime: {t_arena:.2f}s")

    # 5. MATHEMATICAL OPTIMIZER (Pyomo + HiGHS)
    print("\n[STEP 5: MATHEMATICAL MIP OPTIMIZER (Pyomo + HiGHS)]")
    t0 = time.time()
    optimizer = PyomoSupplyChainOptimizer()
    mip_res = optimizer.solve(
        demand_by_product={"FG_SMART_IOT": 1000.0, "FG_TELECOM_NODE": 600.0},
        shortfall_by_product={"FG_SMART_IOT": 400.0, "FG_TELECOM_NODE": 250.0},
        suppliers={
            "SUP_BENGALURU_CHIPS": {"daily_capacity": {"FG_SMART_IOT": 150.0, "FG_TELECOM_NODE": 100.0}, "cost_per_unit": {"FG_SMART_IOT": 3800.0, "FG_TELECOM_NODE": 6200.0}, "is_alternate": True, "lead_time_days": 1.5, "destination_factory": "FAC_PUNE"},
            "SUP_BHILAI_ALLOYS": {"daily_capacity": {"FG_SMART_IOT": 200.0, "FG_TELECOM_NODE": 120.0}, "cost_per_unit": {"FG_SMART_IOT": 3600.0, "FG_TELECOM_NODE": 5900.0}, "is_alternate": True, "lead_time_days": 2.0, "destination_factory": "FAC_SRIPERUMBUDUR"}
        },
        routes={
            "E_JNPT_PUNE": {"origin": "PORT_JNPT", "destination": "FAC_PUNE", "capacity": 300.0, "unit_cost": 150.0, "lead_time": 1.0}
        },
        warehouses={
            "WH_GURGAON": {"inventory": {"FG_SMART_IOT": 700.0, "FG_TELECOM_NODE": 350.0}},
            "WH_BENGALURU": {"inventory": {"FG_SMART_IOT": 600.0, "FG_TELECOM_NODE": 300.0}}
        },
        constraints=RecoveryOptimizationRequest(
            max_budget=1200000.0,
            min_service_level=0.90,
            max_recovery_days=7.0,
            preference="balanced"
        )
    )
    t_mip = time.time() - t0
    print(f"  ✓ Solver:               {mip_res.solver_name} ({mip_res.status})")
    print(f"  ✓ Objective Value:      {mip_res.objective_value:,.2f}")
    print(f"  ✓ Incremental Cost:     ₹{mip_res.incremental_cost/1e5:.1f} Lakhs (Limit: ₹12L)")
    print(f"  ✓ Achieved Service:     {mip_res.achieved_service_level*100:.1f}%")
    print(f"  ✓ Action Decisions:     {len(mip_res.actions)} flow allocations")
    print(f"  ✓ Rationale:            {mip_res.decision_rationale}")
    print(f"  Runtime: {t_mip:.2f}s")

    # 6. WHAT-IF SENSITIVITY EXPLORER
    print("\n[STEP 6: WHAT-IF SENSITIVITY EXPLORER (+30% Demand Surge)]")
    t0 = time.time()
    whatif = WhatIfEngine(seed=42)
    whatif_res = whatif.run_scenario(WhatIfRequest(
        scenario_name="Surge +30% & Port JNPT Capacity 20%",
        demand_multiplier=1.30,
        port_capacity_multiplier=0.20,
        disruption_duration_days=8.0,
        horizon_days=25
    ))
    t_whatif = time.time() - t0
    print(f"  ✓ Baseline Service:     {whatif_res.baseline_metrics.service_level*100:.1f}%")
    print(f"  ✓ What-If Service:      {whatif_res.whatif_metrics.service_level*100:.1f}%")
    print(f"  ✓ Cost Change:          {whatif_res.comparisons['total_cost_inr'].percentage_change:+.1f}%")
    print(f"  ✓ Insight:              {whatif_res.executive_insight}")
    print(f"  Runtime: {t_whatif:.2f}s")

    # 7. MONTE CARLO STRESS TESTING
    print("\n[STEP 7: MONTE CARLO STRESS TEST LAB (100 Randomized Scenarios)]")
    t0 = time.time()
    stress_engine = StressTestEngine(seed=42)
    summary, _ = stress_engine.run_stress_test(runs=100, horizon_days=20)
    t_stress = time.time() - t0
    print(f"  ✓ Total Runs:           {summary.total_scenarios_run}")
    print(f"  ✓ Mean Service Level:   {summary.mean_service_level*100:.1f}% (Worst-Case: {summary.worst_case_service_level*100:.1f}%)")
    print(f"  ✓ P90 Cost Exposure:    ₹{summary.p90_cost_inr/1e5:.1f} Lakhs")
    print(f"  ✓ P95 Recovery Days:    {summary.p95_recovery_days:.1f} days")
    print(f"  Runtime: {t_stress:.2f}s")

    # 8. NETWORK REDESIGN
    print("\n[STEP 8: PROACTIVE NETWORK REDESIGN RESILIENCE PROOF]")
    t0 = time.time()
    redesign_engine = NetworkRedesignEngine(seed=42)
    redesign_res = redesign_engine.evaluate_redesign_resilience(
        config=RedesignConfiguration(
            add_backup_chip_supplier=True,
            add_freight_corridor_bypass=True,
            increase_safety_stock_pct=40.0,
            add_mundra_alternate_port=True
        ),
        stress_runs=50
    )
    t_redesign = time.time() - t0
    print(f"  ✓ Service Retention Gain:       +{redesign_res.service_retention_gain_pct}%")
    print(f"  ✓ P95 Recovery Days Saved:      -{redesign_res.p95_recovery_reduction_days:.1f} days")
    print(f"  ✓ Resilience Score Lift:        +{redesign_res.resilience_score_improvement:.1f} points")
    print(f"  ✓ Criticality Shifts:           JNPT Mumbai: {redesign_res.criticality_shifts[0]['before_score']} -> {redesign_res.criticality_shifts[0]['after_score']} ({redesign_res.criticality_shifts[0]['change']:+.2f})")
    print(f"  ✓ Engineering Verdict:          {redesign_res.engineering_verdict}")
    print(f"  Runtime: {t_redesign:.2f}s")

    total_elapsed = time.time() - start_total_time
    print("=" * 80)
    print(f"PRIMARY DEMO VALIDATION SUCCESSFUL: All 8 steps executed in {total_elapsed:.2f}s total runtime.")
    print("=" * 80)

if __name__ == "__main__":
    run_e2e_validation()
