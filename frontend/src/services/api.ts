import { MetricsReport, NodeItem, EdgeItem, CascadeLinkItem, RecoveryArenaComparisonItem } from '../types'

const API_BASE = '/api'

export const api = {
  async getNetwork(): Promise<{ nodes: NodeItem[]; edges: EdgeItem[]; products: any[] }> {
    const res = await fetch(`${API_BASE}/network`)
    if (!res.ok) throw new Error('Failed to fetch network')
    return res.json()
  },

  async runSimulation(payload: {
    horizon_days?: number
    seed?: number
    disruptions?: any[]
    demand_multiplier?: number
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('Simulation failed')
    return res.json()
  },

  async getSimulation(simId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/${simId}`)
    if (!res.ok) throw new Error('Failed to fetch simulation data')
    return res.json()
  },

  async compareRecovery(payload: {
    disrupted_target_id: string
    unfulfilled_demand_units: number
    disrupted_service_level: number
    daily_loss_inr: number
    max_budget: number
    min_service_level: number
    max_recovery_days: number
    preference: string
  }): Promise<RecoveryArenaComparisonItem> {
    const res = await fetch(`${API_BASE}/recovery/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('Failed to compare recovery options')
    return res.json()
  },

  async optimizeRecovery(payload: {
    max_budget: number
    min_service_level: number
    max_recovery_days: number
    preference: string
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/recovery/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('Optimization failed')
    return res.json()
  },

  async runWhatIf(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/what-if`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('What-if failed')
    return res.json()
  },

  async runStressTest(runs: number = 100): Promise<any> {
    const res = await fetch(`${API_BASE}/stress-test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ runs, horizon_days: 20, seed: 42 })
    })
    if (!res.ok) throw new Error('Stress test failed')
    return res.json()
  },

  async getCriticality(): Promise<any> {
    const res = await fetch(`${API_BASE}/criticality`)
    if (!res.ok) throw new Error('Criticality evaluation failed')
    return res.json()
  },

  async evaluateRedesign(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/redesign`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('Redesign evaluation failed')
    return res.json()
  }
}
