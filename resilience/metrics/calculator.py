from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class MetricsReport(BaseModel):
    # Customer Service KPIs
    total_demand_units: float = 0.0
    fulfilled_demand_units: float = 0.0
    unfulfilled_demand_units: float = 0.0
    service_level: float = Field(..., description="Overall service level (0.0 to 1.0)")
    fill_rate: float = Field(..., description="Order fill rate (0.0 to 1.0)")
    otif_rate: float = Field(..., description="On-Time In-Full percentage (0.0 to 1.0)")

    # Operations KPIs
    total_shipments: int = 0
    delayed_shipments: int = 0
    avg_shipment_delay_days: float = 0.0
    total_stockout_occurrences: int = 0
    total_production_units: float = 0.0

    # Financial KPIs (INR)
    total_transport_cost: float = 0.0
    total_holding_cost: float = 0.0
    total_stockout_penalties: float = 0.0
    total_expedited_costs: float = 0.0
    total_financial_loss: float = 0.0
    gross_revenue: float = 0.0
    net_operating_profit: float = 0.0

    # Resilience Dimensions (The 4 R's: Robustness, Rapidity, Resourcefulness, Redundancy)
    service_retention_score: float = Field(..., description="Percentage of baseline service retained (0-100)")
    time_to_survive_days: float = Field(..., description="Average days buffer survival across critical nodes")
    time_to_recover_days: float = Field(..., description="Days required to restore service level >= 90%")
    performance_drop_pct: float = Field(..., description="Max drop in service level during peak shock")

    # Composite Score
    resilience_score: float = Field(..., description="Transparent CHAINSHIELD composite score (0-100)")
    score_breakdown: Dict[str, float] = Field(default_factory=dict)

def calculate_metrics(
    demand_records: List[Dict[str, Any]],     # [{demand, fulfilled, on_time, revenue, penalty}]
    shipment_records: List[Dict[str, Any]],   # [{cost, delay_days, expedited}]
    daily_inventory_holding_cost: float,
    baseline_service_level: float = 0.98,
    recovery_days: float = 0.0,
    min_tts_days: float = 7.0,
    spare_capacity_ratio: float = 0.25
) -> MetricsReport:
    """
    Computes all operational, customer, financial, and resilience KPIs.
    Computes the transparent CHAINSHIELD Resilience Score based on:
      - 30% Service retention
      - 25% Recovery speed (Rapidity: penalizes high recovery days)
      - 20% Cost stability (penalizes excess penalties / cost inflation)
      - 15% Inventory stability & survival (TTS)
      - 10% Redundancy / spare capacity
    """
    total_demand = sum(d["demand"] for d in demand_records) or 1.0
    fulfilled = sum(d["fulfilled"] for d in demand_records)
    unfulfilled = total_demand - fulfilled
    on_time_units = sum(d["fulfilled"] for d in demand_records if d.get("on_time", True))

    service_lvl = max(0.0, min(1.0, fulfilled / total_demand))
    fill_rate = service_lvl
    otif = max(0.0, min(1.0, on_time_units / total_demand))

    # Shipment stats
    total_shipments = len(shipment_records)
    delayed_shipments = sum(1 for s in shipment_records if s.get("delay_days", 0.0) > 0.05)
    total_delays = sum(s.get("delay_days", 0.0) for s in shipment_records)
    avg_delay = (total_delays / delayed_shipments) if delayed_shipments > 0 else 0.0

    transport_cost = sum(s.get("cost", 0.0) for s in shipment_records)
    expedited_cost = sum(s.get("expedite_surcharge", 0.0) for s in shipment_records)
    stockout_penalties = sum(d.get("penalty", 0.0) for d in demand_records)
    revenue = sum(d.get("revenue", 0.0) for d in demand_records)

    total_cost = transport_cost + daily_inventory_holding_cost + stockout_penalties + expedited_cost
    net_profit = revenue - total_cost

    # Resilience calculations
    perf_drop = max(0.0, (baseline_service_level - service_lvl) / baseline_service_level) * 100.0
    service_retention = max(0.0, (service_lvl / baseline_service_level)) * 100.0

    # 1. Service retention score (0-100)
    w_service = min(100.0, service_retention) * 0.30

    # 2. Recovery speed score (0-100) -> 0 days recovery = 100, 14 days recovery = 0
    recovery_score = max(0.0, 100.0 - (recovery_days * 7.14))
    w_rapidity = recovery_score * 0.25

    # 3. Cost stability score (0-100) -> penalties relative to revenue
    cost_stability = max(0.0, 100.0 - ((stockout_penalties + expedited_cost) / (revenue or 1.0) * 100.0))
    w_cost = min(100.0, cost_stability) * 0.20

    # 4. Inventory survival score (0-100) -> survival >= 7 days = 100%
    tts_score = min(100.0, (min_tts_days / 7.0) * 100.0)
    w_survival = tts_score * 0.15

    # 5. Redundancy score (0-100)
    redundancy_score = min(100.0, spare_capacity_ratio * 400.0)
    w_redundancy = redundancy_score * 0.10

    composite_resilience = round(w_service + w_rapidity + w_cost + w_survival + w_redundancy, 1)

    return MetricsReport(
        total_demand_units=round(total_demand, 1),
        fulfilled_demand_units=round(fulfilled, 1),
        unfulfilled_demand_units=round(unfulfilled, 1),
        service_level=round(service_lvl, 4),
        fill_rate=round(fill_rate, 4),
        otif_rate=round(otif, 4),
        total_shipments=total_shipments,
        delayed_shipments=delayed_shipments,
        avg_shipment_delay_days=round(avg_delay, 2),
        total_stockout_occurrences=sum(1 for d in demand_records if d["fulfilled"] < d["demand"]),
        total_production_units=fulfilled + 500.0, # will be populated by simulation environment
        total_transport_cost=round(transport_cost, 2),
        total_holding_cost=round(daily_inventory_holding_cost, 2),
        total_stockout_penalties=round(stockout_penalties, 2),
        total_expedited_costs=round(expedited_cost, 2),
        total_financial_loss=round(stockout_penalties + expedited_cost, 2),
        gross_revenue=round(revenue, 2),
        net_operating_profit=round(net_profit, 2),
        service_retention_score=round(service_retention, 1),
        time_to_survive_days=round(min_tts_days, 1),
        time_to_recover_days=round(recovery_days, 1),
        performance_drop_pct=round(perf_drop, 1),
        resilience_score=composite_resilience,
        score_breakdown={
            "service_retention": round(w_service, 1),
            "recovery_speed": round(w_rapidity, 1),
            "cost_stability": round(w_cost, 1),
            "inventory_survival": round(w_survival, 1),
            "redundancy": round(w_redundancy, 1)
        }
    )
