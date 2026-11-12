import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_api_network():
    response = client.get("/network")
    assert response.status_code == 200
    data = response.json()
    assert data["node_count"] == 29
    assert len(data["nodes"]) == 29
    assert len(data["edges"]) >= 25

def test_api_simulation_run_and_cascade():
    req_body = {
        "horizon_days": 15,
        "seed": 42,
        "disruptions": [
            {
                "id": "API_DISR_PORT",
                "name": "Port Strike JNPT",
                "disruption_type": "PORT_STRIKE",
                "target_id": "PORT_JNPT",
                "start_day": 3.0,
                "duration_days": 8.0,
                "capacity_multiplier": 0.20,
                "delay_multiplier": 2.5
            }
        ]
    }
    response = client.post("/simulation/run", json=req_body)
    assert response.status_code == 200
    run_res = response.json()
    assert "simulation_id" in run_res
    sim_id = run_res["simulation_id"]

    # Test GET /simulation/{id}/metrics
    metrics_res = client.get(f"/simulation/{sim_id}/metrics")
    assert metrics_res.status_code == 200
    assert "service_level" in metrics_res.json()

    # Test GET /simulation/{id}/cascade
    cascade_res = client.get(f"/simulation/{sim_id}/cascade")
    assert cascade_res.status_code == 200
    assert "chain" in cascade_res.json()

def test_api_recovery_compare_and_optimize():
    comp_res = client.post("/recovery/compare", json={
        "disrupted_target_id": "PORT_JNPT",
        "unfulfilled_demand_units": 600.0,
        "disrupted_service_level": 0.74,
        "daily_loss_inr": 450000.0,
        "max_budget": 1200000.0,
        "min_service_level": 0.90,
        "max_recovery_days": 7.0,
        "preference": "balanced"
    })
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert len(comp_data["strategies"]) == 4
    assert comp_data["best_feasible_strategy"] is not None

    opt_res = client.post("/recovery/optimize", json={
        "max_budget": 1200000.0,
        "min_service_level": 0.90,
        "max_recovery_days": 7.0,
        "preference": "balanced"
    })
    assert opt_res.status_code == 200
    opt_data = opt_res.json()
    assert opt_data["status"] == "OPTIMAL"
    assert len(opt_data["actions"]) > 0

def test_api_whatif():
    whatif_res = client.post("/what-if", json={
        "scenario_name": "API What If Test",
        "demand_multiplier": 1.25,
        "port_capacity_multiplier": 0.30,
        "disruption_duration_days": 6.0,
        "horizon_days": 15
    })
    assert whatif_res.status_code == 200
    assert "comparisons" in whatif_res.json()
