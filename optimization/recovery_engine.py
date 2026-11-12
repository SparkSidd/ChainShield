from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class RecoveryStrategyType(str, Enum):
    REROUTE = "REROUTE"
    ALTERNATE_SUPPLIER = "ALTERNATE_SUPPLIER"
    EXPEDITED_TRANSPORT = "EXPEDITED_TRANSPORT"
    INVENTORY_REALLOCATION = "INVENTORY_REALLOCATION"
    BUFFER_INCREASE = "BUFFER_INCREASE"

class RecoveryAction(BaseModel):
    action_type: RecoveryStrategyType
    target_id: str
    parameter_adjustments: Dict[str, Any] = Field(default_factory=dict)
    description: str

class EvaluatedStrategy(BaseModel):
    strategy_id: str
    name: str
    strategy_type: RecoveryStrategyType
    description: str
    incremental_cost_inr: float
    expected_recovery_days: float
    expected_service_level: float
    stockout_reduction_units: float
    feasible: bool = True
    infeasibility_reasons: List[str] = Field(default_factory=list)
    resilience_gain_pct: float = 0.0

class ConstraintDrivenOptimizer:
    """
    Evaluates candidate recovery options against operational constraints:
      - max_additional_cost (INR)
      - min_service_level (0.0 - 1.0)
      - max_recovery_days (days)
    Produces a transparent comparison matrix and identifies the optimal feasible recovery plan.
    """
    def __init__(
        self,
        max_additional_cost: float = 1200000.0,  # ₹12 Lakhs
        min_service_level: float = 0.90,         # 90%
        max_recovery_days: float = 7.0           # 7 days
    ):
        self.max_additional_cost = max_additional_cost
        self.min_service_level = min_service_level
        self.max_recovery_days = max_recovery_days

    def generate_candidate_strategies(
        self,
        disrupted_target_id: str,
        unfulfilled_demand_units: float,
        daily_loss_inr: float
    ) -> List[EvaluatedStrategy]:
        """
        Generates standard candidate recovery strategies for the disrupted node/corridor:
          1. Alternate Supplier Activation
          2. Multimodal Rerouting
          3. Expedited Priority Air/Express Transit
          4. Inter-Warehouse Inventory Buffer Reallocation
        """
        candidates = [
            EvaluatedStrategy(
                strategy_id="REC_ALT_SUPPLIER",
                name="Activate Domestic Backup Supplier (Bengaluru & Bhilai)",
                strategy_type=RecoveryStrategyType.ALTERNATE_SUPPLIER,
                description="Shift 60% of component procurement to domestic Tier-1 suppliers, bypassing maritime port choke.",
                incremental_cost_inr=850000.0,      # ₹8.5 Lakhs
                expected_recovery_days=5.0,         # 5 days
                expected_service_level=0.925,       # 92.5%
                stockout_reduction_units=round(unfulfilled_demand_units * 0.80, 0),
                resilience_gain_pct=18.5
            ),
            EvaluatedStrategy(
                strategy_id="REC_REROUTE_RAIL",
                name="Multimodal Reroute via Chennai Port Rail Corridor",
                strategy_type=RecoveryStrategyType.REROUTE,
                description="Divert delayed containers through southern rail corridor directly to Pune and Manesar assembly plants.",
                incremental_cost_inr=680000.0,      # ₹6.8 Lakhs
                expected_recovery_days=8.5,         # 8.5 days (fails max 7 day constraint!)
                expected_service_level=0.880,       # 88.0% (fails 90% service level target)
                stockout_reduction_units=round(unfulfilled_demand_units * 0.65, 0),
                resilience_gain_pct=12.0
            ),
            EvaluatedStrategy(
                strategy_id="REC_EXPEDITE_AIR",
                name="Emergency Expedited Air Freight",
                strategy_type=RecoveryStrategyType.EXPEDITED_TRANSPORT,
                description="Charter dedicated priority air cargo for microcontrollers directly to Pune plant within 48 hours.",
                incremental_cost_inr=1850000.0,     # ₹18.5 Lakhs (fails budget constraint!)
                expected_recovery_days=2.5,         # 2.5 days (fastest)
                expected_service_level=0.965,       # 96.5%
                stockout_reduction_units=round(unfulfilled_demand_units * 0.95, 0),
                resilience_gain_pct=24.0
            ),
            EvaluatedStrategy(
                strategy_id="REC_WH_REALLOCATION",
                name="Cross-Regional Inventory Buffer Transfer",
                strategy_type=RecoveryStrategyType.INVENTORY_REALLOCATION,
                description="Reallocate safety stock from South (Bengaluru) and North (Gurgaon) hubs to cover western shortfall.",
                incremental_cost_inr=420000.0,      # ₹4.2 Lakhs
                expected_recovery_days=6.0,         # 6 days
                expected_service_level=0.908,       # 90.8%
                stockout_reduction_units=round(unfulfilled_demand_units * 0.72, 0),
                resilience_gain_pct=15.0
            )
        ]

        # Evaluate feasibility against constraints
        for s in candidates:
            reasons = []
            if s.incremental_cost_inr > self.max_additional_cost:
                reasons.append(f"Cost ₹{s.incremental_cost_inr:,.0f} exceeds budget limit of ₹{self.max_additional_cost:,.0f}")
            if s.expected_service_level < self.min_service_level:
                reasons.append(f"Service level {s.expected_service_level*100:.1f}% is below minimum target {self.min_service_level*100:.1f}%")
            if s.expected_recovery_days > self.max_recovery_days:
                reasons.append(f"Recovery time {s.expected_recovery_days:.1f} days exceeds max allowance of {self.max_recovery_days:.1f} days")

            if reasons:
                s.feasible = False
                s.infeasibility_reasons = reasons

        return candidates

    def optimize_recovery(
        self,
        candidates: List[EvaluatedStrategy],
        preference: str = "balanced"  # "cost_first", "service_first", "recovery_first", "balanced"
    ) -> Dict[str, Any]:
        """
        Ranks feasible options and returns the recommended strategy with explainable rationale.
        """
        feasible = [s for s in candidates if s.feasible]

        if not feasible:
            return {
                "status": "INFEASIBLE",
                "recommended_strategy": None,
                "explanation": "No candidate recovery strategy satisfies all constraints simultaneously (budget, minimum service level, and recovery deadline). Consider relaxing the budget ceiling or allowing extended recovery duration.",
                "all_strategies": [s.model_dump() for s in candidates]
            }

        # Ranking score formulation
        def score_strategy(s: EvaluatedStrategy) -> float:
            cost_norm = 1.0 - (s.incremental_cost_inr / max(self.max_additional_cost, 1.0))
            service_norm = s.expected_service_level
            speed_norm = 1.0 - (s.expected_recovery_days / max(self.max_recovery_days, 1.0))

            if preference == "cost_first":
                return (0.60 * cost_norm) + (0.25 * service_norm) + (0.15 * speed_norm)
            elif preference == "service_first":
                return (0.20 * cost_norm) + (0.60 * service_norm) + (0.20 * speed_norm)
            elif preference == "recovery_first":
                return (0.20 * cost_norm) + (0.20 * service_norm) + (0.60 * speed_norm)
            else:  # balanced
                return (0.35 * cost_norm) + (0.40 * service_norm) + (0.25 * speed_norm)

        ranked = sorted(feasible, key=score_strategy, reverse=True)
        winner = ranked[0]

        explanation = (
            f"Strategy '{winner.name}' is recommended under '{preference}' preference. "
            f"It delivers {winner.expected_service_level*100:.1f}% service level with {winner.expected_recovery_days:.1f} days recovery "
            f"at ₹{winner.incremental_cost_inr:,.0f} incremental cost, staying within the ₹{self.max_additional_cost:,.0f} budget."
        )

        return {
            "status": "OPTIMAL",
            "recommended_strategy": winner.model_dump(),
            "explanation": explanation,
            "all_strategies": [s.model_dump() for s in candidates],
            "feasible_count": len(feasible),
            "infeasible_count": len(candidates) - len(feasible)
        }
