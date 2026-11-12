import pytest
from optimization.recovery_arena import RecoveryArenaService

def test_recovery_arena_comparison():
    arena = RecoveryArenaService()
    comparison = arena.compare_strategies(
        disrupted_target_id="PORT_JNPT",
        unfulfilled_demand_units=600.0,
        disrupted_service_level=0.74,
        daily_loss_inr=450000.0,
        max_budget=1200000.0,  # ₹12 Lakhs
        min_service_level=0.90, # 90%
        max_recovery_days=7.0,   # 7 days
        preference="balanced"
    )

    assert len(comparison.strategies) == 4
    assert len(comparison.pareto_frontier) == 4

    # Check Pareto optimality flags
    pareto_opt_count = sum(1 for p in comparison.pareto_frontier if p.is_pareto_optimal)
    assert pareto_opt_count >= 2

    # Under budget ₹12L, service >= 90%, recovery <= 7 days:
    # Alternate supplier (₹8.5L, 92.5%, 5d) and WH Reallocation (₹4.2L, 90.8%, 6d) are feasible
    # Expedite (₹18.5L > ₹12L) is infeasible
    # Reroute (8.5d > 7d, 88% < 90%) is infeasible
    assert comparison.best_feasible_strategy is not None
    assert comparison.best_feasible_strategy.feasible is True
    assert comparison.best_feasible_strategy.strategy_id in ["REC_ALT_SUPPLIER", "REC_WH_REALLOCATION"]

    # Infeasible test
    infeasible_comp = arena.compare_strategies(
        disrupted_target_id="PORT_JNPT",
        unfulfilled_demand_units=600.0,
        disrupted_service_level=0.74,
        daily_loss_inr=450000.0,
        max_budget=300000.0, # ₹3 Lakhs - too low for any strategy
        min_service_level=0.95,
        max_recovery_days=3.0
    )
    assert infeasible_comp.best_feasible_strategy is None
    assert "INFEASIBLE" in infeasible_comp.executive_recommendation
