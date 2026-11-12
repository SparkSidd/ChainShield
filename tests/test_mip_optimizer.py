import pytest
from optimization.mip_solver import PyomoSupplyChainOptimizer, RecoveryOptimizationRequest

def test_pyomo_highs_optimal_solve():
    optimizer = PyomoSupplyChainOptimizer()

    demand = {"RM_CHIP": 1000.0, "RM_CHASSIS": 800.0}
    shortfall = {"RM_CHIP": 400.0, "RM_CHASSIS": 250.0}

    suppliers = {
        "SUP_BENGALURU_CHIPS": {
            "daily_capacity": {"RM_CHIP": 250.0},
            "cost_per_unit": {"RM_CHIP": 1300.0},
            "is_alternate": True,
            "lead_time_days": 1.5,
            "destination_factory": "FAC_PUNE"
        },
        "SUP_CHENNAI_METALS": {
            "daily_capacity": {"RM_CHASSIS": 300.0},
            "cost_per_unit": {"RM_CHASSIS": 850.0},
            "is_alternate": True,
            "lead_time_days": 1.0,
            "destination_factory": "FAC_SRIPERUMBUDUR"
        }
    }

    routes = {
        "E_BLR_PUNE": {
            "origin": "SUP_BENGALURU_CHIPS",
            "destination": "FAC_PUNE",
            "capacity": 300.0,
            "unit_cost": 500.0,
            "lead_time": 2.0
        }
    }

    warehouses = {
        "WH_GURGAON": {"inventory": {"RM_CHIP": 500.0, "RM_CHASSIS": 600.0}},
        "WH_MUMBAI": {"inventory": {"RM_CHIP": 100.0, "RM_CHASSIS": 100.0}}
    }

    req = RecoveryOptimizationRequest(
        max_budget=1200000.0,  # ₹12 Lakhs
        min_service_level=0.90, # 90%
        max_recovery_days=7.0,
        preference="balanced"
    )

    result = optimizer.solve(
        demand_by_product=demand,
        shortfall_by_product=shortfall,
        suppliers=suppliers,
        routes=routes,
        warehouses=warehouses,
        constraints=req
    )

    assert result.status == "OPTIMAL"
    assert result.solver_name == "HiGHS"
    assert result.achieved_service_level >= 0.90
    assert result.incremental_cost <= 1200000.0
    assert len(result.actions) > 0
    assert result.constraint_status["budget_satisfied"] is True
    assert result.constraint_status["service_satisfied"] is True

def test_pyomo_highs_infeasible_budget():
    optimizer = PyomoSupplyChainOptimizer()

    demand = {"RM_CHIP": 1000.0}
    shortfall = {"RM_CHIP": 800.0}

    suppliers = {
        "SUP_BENGALURU_CHIPS": {
            "daily_capacity": {"RM_CHIP": 250.0},
            "cost_per_unit": {"RM_CHIP": 1500.0},
            "is_alternate": True,
            "lead_time_days": 2.0,
            "destination_factory": "FAC_PUNE"
        }
    }

    routes = {
        "E_BLR_PUNE": {"origin": "SUP_BLR", "destination": "FAC_PUNE", "capacity": 200.0, "unit_cost": 300.0, "lead_time": 2.0}
    }

    warehouses = {"WH_GURGAON": {"inventory": {"RM_CHIP": 0.0}}}

    # Setting an impossibly low budget: ₹5,000 for ₹800k worth of required inventory at 95% service level
    req = RecoveryOptimizationRequest(
        max_budget=5000.0,
        min_service_level=0.95,
        max_recovery_days=7.0
    )

    result = optimizer.solve(
        demand_by_product=demand,
        shortfall_by_product=shortfall,
        suppliers=suppliers,
        routes=routes,
        warehouses=warehouses,
        constraints=req
    )

    assert result.status == "INFEASIBLE"
    assert len(result.rejected_reasons) > 0
    assert result.constraint_status["satisfied"] is False
