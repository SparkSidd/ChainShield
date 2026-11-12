from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

from backend.app.schemas import (
    SimulationRunRequest,
    SimulationRunResponse,
    RecoveryCompareRequest,
    StressTestRunRequest
)
from backend.app.services import BackendServiceManager
from optimization.mip_solver import RecoveryOptimizationRequest
from engine.whatif.whatif_engine import WhatIfRequest
from engine.redesign.redesign_engine import RedesignConfiguration

app = FastAPI(
    title="CHAINSHIELD API",
    description="Dynamic Supply Chain Recovery & Resilience Simulator Backend Engine",
    version="1.0.0"
)

# Enable CORS for React/Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "product": "CHAINSHIELD", "version": "1.0.0"}

@app.get("/network")
def get_network():
    """Returns complete multi-echelon network topology with nodes, edges, products and positions."""
    return BackendServiceManager.get_network_topology()

@app.post("/simulation/run")
def run_simulation(req: SimulationRunRequest):
    """Executes a discrete-event SimPy simulation run with optional disruption injection."""
    run_data = BackendServiceManager.execute_simulation(req)
    return {
        "simulation_id": run_data["simulation_id"],
        "horizon_days": run_data["horizon_days"],
        "seed": run_data["seed"],
        "metrics": run_data["metrics"],
        "event_count": len(run_data["events"]),
        "cascade_step_count": len(run_data["cascade"]["chain"]),
        "cascade": run_data["cascade"],
        "daily_timeseries": run_data["daily_timeseries"]
    }

@app.get("/simulation/{sim_id}")
def get_simulation(sim_id: str):
    """Retrieves cached telemetry and metrics for a specific simulation run."""
    data = BackendServiceManager.get_simulation_run(sim_id)
    if not data:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return data

@app.get("/simulation/{sim_id}/metrics")
def get_simulation_metrics(sim_id: str):
    """Returns operational, customer, financial and resilience metrics for a simulation run."""
    data = BackendServiceManager.get_simulation_run(sim_id)
    if not data:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return data["metrics"]

@app.get("/simulation/{sim_id}/events")
def get_simulation_events(sim_id: str):
    """Returns discrete event log for a simulation run."""
    data = BackendServiceManager.get_simulation_run(sim_id)
    if not data:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return {"simulation_id": sim_id, "events": data["events"]}

@app.get("/simulation/{sim_id}/cascade")
def get_simulation_cascade(sim_id: str):
    """Returns causal cascade propagation graph and time-to-survive records."""
    data = BackendServiceManager.get_simulation_run(sim_id)
    if not data:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return data["cascade"]

@app.post("/recovery/compare")
def compare_recovery_strategies(req: RecoveryCompareRequest):
    """Compares candidate recovery options (Backup Supplier, Rerouting, Expediting, Reallocation) with Pareto frontier."""
    return BackendServiceManager.compare_recovery(
        disrupted_target=req.disrupted_target_id,
        unfulfilled_units=req.unfulfilled_demand_units,
        service_lvl=req.disrupted_service_level,
        daily_loss=req.daily_loss_inr,
        max_budget=req.max_budget,
        min_service=req.min_service_level,
        max_recovery_days=req.max_recovery_days,
        preference=req.preference
    )

@app.post("/recovery/optimize")
def optimize_recovery_plan(req: RecoveryOptimizationRequest):
    """Solves multi-echelon recovery flow optimization using Pyomo + HiGHS solver under explicit constraints."""
    return BackendServiceManager.solve_mip_optimization(req)

@app.post("/what-if")
def run_what_if_scenario(req: WhatIfRequest):
    """Runs counterfactual What-If parameter sensitivity analysis against baseline."""
    return BackendServiceManager.run_whatif(req)

@app.post("/stress-test")
def run_stress_testing_lab(req: StressTestRunRequest):
    """Executes Monte Carlo stress testing (100-1000 randomized disruption runs) with statistical loss distributions."""
    return BackendServiceManager.run_stress_test(
        runs=req.runs,
        horizon_days=req.horizon_days,
        seed=req.seed
    )

@app.get("/criticality")
def get_criticality_rankings():
    """Returns ranked criticality for suppliers, factories, ports, warehouses, routes and compares failure modes."""
    return BackendServiceManager.get_criticality()

@app.post("/redesign")
def evaluate_network_redesign(config: RedesignConfiguration):
    """Evaluates before-and-after resilience gains under architectural network redesigns."""
    return BackendServiceManager.run_redesign(config)
