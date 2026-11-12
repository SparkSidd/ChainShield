import copy
import random
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

from data.generator import create_baseline_network
from engine.network.network import SupplyChainNetwork
from engine.demand.generator import DemandGenerator, DemandSurge
from engine.simulation.environment import SupplyChainSimulator
from resilience.disruptions.disruption import Disruption, DisruptionType
from resilience.metrics.calculator import MetricsReport

class ScenarioResult(BaseModel):
    scenario_id: int
    target_id: str
    target_type: str
    disruption_type: DisruptionType
    severity_pct: float
    duration_days: float
    total_cost_inr: float
    service_level: float
    stockout_units: float
    recovery_days: float
    resilience_score: float

class StressTestSummary(BaseModel):
    total_scenarios_run: int
    seed: int
    mean_cost_inr: float
    p50_cost_inr: float
    p90_cost_inr: float
    p95_cost_inr: float
    mean_service_level: float
    worst_case_service_level: float
    mean_recovery_days: float
    p95_recovery_days: float
    mean_resilience_score: float
    loss_distribution_buckets: List[Dict[str, Any]]
    top_vulnerable_targets: List[Dict[str, Any]]

class StressTestEngine:
    """
    Monte Carlo stress test engine running 100 - 1000 randomized disruption simulations
    with deterministic seed reproduction.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def run_stress_test(
        self,
        runs: int = 100,
        horizon_days: int = 20,
        custom_network: Optional[SupplyChainNetwork] = None
    ) -> Tuple[StressTestSummary, List[ScenarioResult]]:
        base_net = custom_network or create_baseline_network(seed=self.seed)
        demand_gen = DemandGenerator(seed=self.seed)
        cust_profiles = {c_id: c.demand_profiles for c_id, c in base_net.get_customers().items()}
        base_schedule = demand_gen.generate_schedule(customer_profiles=cust_profiles, horizon_days=horizon_days)

        # Candidate targets
        node_candidates = [
            (p_id, "PORT", DisruptionType.PORT_STRIKE) for p_id in base_net.get_ports()
        ] + [
            (s_id, "SUPPLIER", DisruptionType.SUPPLIER_FAILURE) for s_id in base_net.get_suppliers()
        ] + [
            (f_id, "FACTORY", DisruptionType.VEHICLE_BREAKDOWN) for f_id in base_net.get_factories()
        ] + [
            (w_id, "WAREHOUSE", DisruptionType.SHIPMENT_DELAY) for w_id in base_net.get_warehouses()
        ]

        results: List[ScenarioResult] = []
        target_damage: Dict[str, List[float]] = {}

        for i in range(1, runs + 1):
            target_id, target_type, disr_type = self.rng.choice(node_candidates)
            start_day = self.rng.uniform(2.0, max(3.0, horizon_days - 10.0))
            duration = self.rng.uniform(3.0, 9.0)
            severity = self.rng.uniform(0.3, 0.9)  # 30% to 90% capacity loss
            demand_mult = self.rng.uniform(0.9, 1.25)

            # Build fresh network copy
            net = copy.deepcopy(custom_network) if custom_network else create_baseline_network(seed=self.seed + i)
            sim = SupplyChainSimulator(network=net, horizon_days=horizon_days, seed=self.seed + i)

            disr = Disruption(
                id=f"DISR_MC_{i}",
                name=f"Random Shock #{i}",
                disruption_type=disr_type,
                target_id=target_id,
                start_day=start_day,
                duration_days=duration,
                capacity_multiplier=round(1.0 - severity, 2),
                delay_multiplier=round(1.0 + severity * 2.0, 2)
            )
            sim.add_disruption(disr)

            # Adjust schedule for demand mult
            run_sched = {}
            for d, custs in base_schedule.items():
                if d <= horizon_days:
                    run_sched[d] = {}
                    for cid, prods in custs.items():
                        run_sched[d][cid] = {p: q * demand_mult for p, q in prods.items()}

            report, _ = sim.run(demand_schedule=run_sched)

            scen_res = ScenarioResult(
                scenario_id=i,
                target_id=target_id,
                target_type=target_type,
                disruption_type=disr_type,
                severity_pct=round(severity * 100, 1),
                duration_days=round(duration, 1),
                total_cost_inr=round(report.total_transport_cost + report.total_holding_cost + report.total_financial_loss, 2),
                service_level=report.service_level,
                stockout_units=report.unfulfilled_demand_units,
                recovery_days=report.time_to_recover_days,
                resilience_score=report.resilience_score
            )
            results.append(scen_res)

            if target_id not in target_damage:
                target_damage[target_id] = []
            target_damage[target_id].append(1.0 - report.service_level)

        # Statistical Aggregations
        costs = [r.total_cost_inr for r in results]
        services = [r.service_level for r in results]
        recoveries = [r.recovery_days for r in results]
        resilience_scores = [r.resilience_score for r in results]

        # Histogram buckets
        min_c, max_c = min(costs), max(costs)
        hist, bin_edges = np.histogram(costs, bins=5)
        buckets = []
        for b_idx in range(len(hist)):
            buckets.append({
                "range_inr": f"₹{bin_edges[b_idx]/1e5:.1f}L - ₹{bin_edges[b_idx+1]/1e5:.1f}L",
                "frequency": int(hist[b_idx])
            })

        # Top vulnerable targets
        vulnerable = []
        for t_id, losses in target_damage.items():
            avg_loss = sum(losses) / len(losses)
            vulnerable.append({
                "target_id": t_id,
                "avg_service_loss_pct": round(avg_loss * 100, 1),
                "runs_evaluated": len(losses)
            })
        vulnerable.sort(key=lambda x: x["avg_service_loss_pct"], reverse=True)

        summary = StressTestSummary(
            total_scenarios_run=runs,
            seed=self.seed,
            mean_cost_inr=round(float(np.mean(costs)), 2),
            p50_cost_inr=round(float(np.percentile(costs, 50)), 2),
            p90_cost_inr=round(float(np.percentile(costs, 90)), 2),
            p95_cost_inr=round(float(np.percentile(costs, 95)), 2),
            mean_service_level=round(float(np.mean(services)), 4),
            worst_case_service_level=round(float(min(services)), 4),
            mean_recovery_days=round(float(np.mean(recoveries)), 1),
            p95_recovery_days=round(float(np.percentile(recoveries, 95)), 1),
            mean_resilience_score=round(float(np.mean(resilience_scores)), 1),
            loss_distribution_buckets=buckets,
            top_vulnerable_targets=vulnerable[:5]
        )

        return summary, results
