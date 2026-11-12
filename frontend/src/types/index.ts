export type ScreenType =
  | 'control-center'
  | 'network'
  | 'disruption-lab'
  | 'cascade-trace'
  | 'recovery-arena'
  | 'stress-test'
  | 'criticality'
  | 'what-if'
  | 'redesign'

export interface MetricsReport {
  total_demand_units: number
  fulfilled_demand_units: number
  unfulfilled_demand_units: number
  service_level: number
  fill_rate: number
  otif_rate: number
  total_shipments: number
  delayed_shipments: number
  avg_shipment_delay_days: number
  total_stockout_occurrences: number
  total_production_units: number
  total_transport_cost: number
  total_holding_cost: number
  total_stockout_penalties: number
  total_expedited_costs: number
  total_financial_loss: number
  gross_revenue: number
  net_operating_profit: number
  service_retention_score: number
  time_to_survive_days: number
  time_to_recover_days: number
  performance_drop_pct: number
  resilience_score: number
  score_breakdown: Record<string, number>
}

export interface NodeItem {
  id: string
  name: string
  type: string
  city: string
  state: string
  lat: number
  lng: number
  criticality: number
  active: boolean
}

export interface EdgeItem {
  id: string
  origin: string
  destination: string
  mode: string
  capacity: number
  lead_time_days: number
  cost_per_unit_km: number
  distance_km: number
  active: boolean
  disrupted: boolean
}

export interface CascadeLinkItem {
  id: string
  timestamp: number
  source_node_or_edge: string
  target_node: string
  cause_event_id?: string
  cause_description: string
  effect_type: string
  magnitude: number
  magnitude_unit: string
  downstream_impact_summary: string
}

export interface EvaluatedStrategyItem {
  strategy_id: string
  name: string
  strategy_type: string
  description: string
  incremental_cost_inr: number
  expected_recovery_days: number
  expected_service_level: number
  stockout_reduction_units: number
  feasible: boolean
  infeasibility_reasons: string[]
  resilience_gain_pct: number
}

export interface ParetoPointItem {
  strategy_id: string
  name: string
  cost_inr: number
  recovery_days: number
  service_level: number
  is_pareto_optimal: boolean
}

export interface RecoveryArenaComparisonItem {
  baseline_disrupted_service: number
  baseline_disrupted_loss_inr: number
  unfulfilled_demand_units: number
  strategies: EvaluatedStrategyItem[]
  pareto_frontier: ParetoPointItem[]
  user_constraints: Record<string, any>
  best_feasible_strategy?: EvaluatedStrategyItem
  mathematical_mip_plan?: any
  executive_recommendation: string
}
