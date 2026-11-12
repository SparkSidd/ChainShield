import uuid
from typing import Dict, Any, Optional
from data.generator import create_baseline_network
from engine.demand.generator import DemandGenerator
from engine.simulation.environment import SupplyChainSimulator
from optimization.recovery_arena import RecoveryArenaService
from optimization.mip_solver import PyomoSupplyChainOptimizer, RecoveryOptimizationRequest
from resilience.stress_testing.stress_lab import StressTestEngine
from resilience.criticality.criticality_engine import CriticalityEngine
from engine.whatif.whatif_engine import WhatIfEngine, WhatIfRequest
from engine.redesign.redesign_engine import NetworkRedesignEngine, RedesignConfiguration
from backend.app.schemas import SimulationRunRequest

# In-memory store for simulation runs
_SIMULATION_STORE: Dict[str, Dict[str, Any]] = {}

class BackendServiceManager:
    @staticmethod
    def get_network_topology() -> Dict[str, Any]:
        net = create_baseline_network(seed=42)
        return net.to_dict()

    @staticmethod
    def execute_simulation(req: SimulationRunRequest) -> Dict[str, Any]:
        sim_id = f"sim_{uuid.uuid4().hex[:8]}"
        net = create_baseline_network(seed=req.seed)
        demand_gen = DemandGenerator(seed=req.seed)
        profiles = {c_id: c.demand_profiles for c_id, c in net.get_customers().items()}
        schedule = demand_gen.generate_schedule(customer_profiles=profiles, horizon_days=req.horizon_days)

        if req.demand_multiplier != 1.0:
            for d in schedule:
                for c in schedule[d]:
                    for p in schedule[d][c]:
                        schedule[d][c][p] = round(schedule[d][c][p] * req.demand_multiplier, 1)

        sim = SupplyChainSimulator(network=net, horizon_days=req.horizon_days, seed=req.seed)
        for disr in req.disruptions:
            sim.add_disruption(disr)

        report, telemetry = sim.run(demand_schedule=schedule)

        run_data = {
            "simulation_id": sim_id,
            "horizon_days": req.horizon_days,
            "seed": req.seed,
            "metrics": report.model_dump(),
            "events": telemetry["events"],
            "cascade": telemetry["cascade"],
            "daily_timeseries": telemetry["daily_timeseries"],
            "final_inventories": telemetry["final_inventories"]
        }
        _SIMULATION_STORE[sim_id] = run_data
        return run_data

    @staticmethod
    def get_simulation_run(sim_id: str) -> Optional[Dict[str, Any]]:
        return _SIMULATION_STORE.get(sim_id)

    @staticmethod
    def compare_recovery(
        disrupted_target: str,
        unfulfilled_units: float,
        service_lvl: float,
        daily_loss: float,
        max_budget: float,
        min_service: float,
        max_recovery_days: float,
        preference: str
    ) -> Dict[str, Any]:
        arena = RecoveryArenaService()
        res = arena.compare_strategies(
            disrupted_target_id=disrupted_target,
            unfulfilled_demand_units=unfulfilled_units,
            disrupted_service_level=service_lvl,
            daily_loss_inr=daily_loss,
            max_budget=max_budget,
            min_service_level=min_service,
            max_recovery_days=max_recovery_days,
            preference=preference
        )
        return res.model_dump()

    @staticmethod
    def solve_mip_optimization(req: RecoveryOptimizationRequest) -> Dict[str, Any]:
        optimizer = PyomoSupplyChainOptimizer()
        demand = {"FG_SMART_IOT": 1200.0, "FG_TELECOM_NODE": 600.0, "FG_CONTROLLER": 800.0}
        shortfall = {"FG_SMART_IOT": 500.0, "FG_TELECOM_NODE": 280.0, "FG_CONTROLLER": 320.0}

        suppliers = {
            "SUP_BENGALURU_CHIPS": {
                "daily_capacity": {"FG_SMART_IOT": 150.0, "FG_TELECOM_NODE": 100.0, "FG_CONTROLLER": 120.0},
                "cost_per_unit": {"FG_SMART_IOT": 3800.0, "FG_TELECOM_NODE": 6200.0, "FG_CONTROLLER": 4700.0},
                "is_alternate": True,
                "lead_time_days": 1.5,
                "destination_factory": "FAC_PUNE"
            },
            "SUP_BHILAI_ALLOYS": {
                "daily_capacity": {"FG_SMART_IOT": 200.0, "FG_TELECOM_NODE": 120.0, "FG_CONTROLLER": 150.0},
                "cost_per_unit": {"FG_SMART_IOT": 3600.0, "FG_TELECOM_NODE": 5900.0, "FG_CONTROLLER": 4600.0},
                "is_alternate": True,
                "lead_time_days": 2.0,
                "destination_factory": "FAC_SRIPERUMBUDUR"
            }
        }

        routes = {
            "E_JNPT_PUNE": {"origin": "PORT_JNPT", "destination": "FAC_PUNE", "capacity": 300.0, "unit_cost": 150.0, "lead_time": 1.0},
            "E_CHENNAI_PUNE": {"origin": "PORT_CHENNAI", "destination": "FAC_PUNE", "capacity": 400.0, "unit_cost": 450.0, "lead_time": 2.5}
        }

        warehouses = {
            "WH_GURGAON": {"inventory": {"FG_SMART_IOT": 700.0, "FG_TELECOM_NODE": 350.0, "FG_CONTROLLER": 450.0}},
            "WH_BENGALURU": {"inventory": {"FG_SMART_IOT": 600.0, "FG_TELECOM_NODE": 300.0, "FG_CONTROLLER": 400.0}}
        }

        res = optimizer.solve(
            demand_by_product=demand,
            shortfall_by_product=shortfall,
            suppliers=suppliers,
            routes=routes,
            warehouses=warehouses,
            constraints=req
        )
        return res.model_dump()

    @staticmethod
    def run_whatif(req: WhatIfRequest) -> Dict[str, Any]:
        engine = WhatIfEngine(seed=req.seed)
        res = engine.run_scenario(req)
        return res.model_dump()

    @staticmethod
    def run_stress_test(runs: int, horizon_days: int, seed: int) -> Dict[str, Any]:
        engine = StressTestEngine(seed=seed)
        summary, scens = engine.run_stress_test(runs=runs, horizon_days=horizon_days)
        return {
            "summary": summary.model_dump(),
            "sample_scenarios": [s.model_dump() for s in scens[:25]]
        }

    @staticmethod
    def get_criticality() -> Dict[str, Any]:
        engine = CriticalityEngine(seed=42)
        report = engine.run_criticality_analysis()
        return report.model_dump()

    @staticmethod
    def run_redesign(config: RedesignConfiguration) -> Dict[str, Any]:
        engine = NetworkRedesignEngine(seed=42)
        res = engine.evaluate_redesign_resilience(config=config, stress_runs=20)
        return res.model_dump()
