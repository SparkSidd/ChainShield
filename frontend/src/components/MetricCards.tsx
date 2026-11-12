import React from 'react'
import { MetricsReport } from '../types'
import { TrendingUp, TrendingDown, Clock, AlertTriangle, ShieldCheck, IndianRupee } from 'lucide-react'

interface MetricCardsProps {
  metrics: MetricsReport | null
  loading?: boolean
}

export const MetricCards: React.FC<MetricCardsProps> = ({ metrics, loading }) => {
  if (loading || !metrics) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 animate-pulse">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-28 bg-slate-800/40 rounded-xl border border-slate-800" />
        ))}
      </div>
    )
  }

  const servicePct = (metrics.service_level * 100).toFixed(1)
  const isServiceHealthy = metrics.service_level >= 0.90

  const totalCostLakhs = (
    (metrics.total_transport_cost + metrics.total_holding_cost + metrics.total_financial_loss) / 100000
  ).toFixed(1)

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      {/* 1. SERVICE LEVEL */}
      <div className={`p-4 rounded-xl border transition-all ${
        isServiceHealthy 
          ? 'bg-slate-900/80 border-slate-800 hover:border-emerald-500/40' 
          : 'bg-rose-950/20 border-rose-800/60 glow-red'
      }`}>
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="font-medium tracking-wide">SERVICE LEVEL</span>
          {isServiceHealthy ? (
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          ) : (
            <TrendingDown className="w-4 h-4 text-rose-400" />
          )}
        </div>
        <div className="flex items-baseline space-x-1">
          <span className={`text-2xl font-bold font-mono ${isServiceHealthy ? 'text-emerald-400' : 'text-rose-400'}`}>
            {servicePct}%
          </span>
          <span className="text-xs text-slate-500">OTIF: {(metrics.otif_rate * 100).toFixed(0)}%</span>
        </div>
        <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${isServiceHealthy ? 'bg-emerald-500' : 'bg-rose-500'}`}
            style={{ width: `${Math.min(100, Math.max(0, metrics.service_level * 100))}%` }}
          />
        </div>
      </div>

      {/* 2. TOTAL COST */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 transition-all">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="font-medium tracking-wide">TOTAL OPERATING COST</span>
          <IndianRupee className="w-4 h-4 text-blue-400" />
        </div>
        <div className="flex items-baseline space-x-1">
          <span className="text-2xl font-bold font-mono text-white">₹{totalCostLakhs}L</span>
        </div>
        <p className="text-xs text-slate-400 mt-2 truncate">
          Penalties: ₹{(metrics.total_stockout_penalties / 1000).toFixed(0)}k
        </p>
      </div>

      {/* 3. RECOVERY TIME */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-amber-500/40 transition-all">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="font-medium tracking-wide">RECOVERY TIME (TTR)</span>
          <Clock className="w-4 h-4 text-amber-400" />
        </div>
        <div className="flex items-baseline space-x-1">
          <span className="text-2xl font-bold font-mono text-amber-300">
            {metrics.time_to_recover_days.toFixed(1)} <span className="text-sm font-normal">days</span>
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Time-to-Survive: <span className="text-slate-200 font-mono">{metrics.time_to_survive_days}d</span>
        </p>
      </div>

      {/* 4. STOCKOUTS */}
      <div className={`p-4 rounded-xl border transition-all ${
        metrics.unfulfilled_demand_units > 0 
          ? 'bg-rose-950/20 border-rose-800/60' 
          : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
      }`}>
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="font-medium tracking-wide">STOCKOUT UNITS</span>
          <AlertTriangle className={`w-4 h-4 ${metrics.unfulfilled_demand_units > 0 ? 'text-rose-400' : 'text-slate-500'}`} />
        </div>
        <div className="flex items-baseline space-x-1">
          <span className={`text-2xl font-bold font-mono ${metrics.unfulfilled_demand_units > 0 ? 'text-rose-400' : 'text-slate-200'}`}>
            {metrics.unfulfilled_demand_units.toFixed(0)}
          </span>
          <span className="text-xs text-slate-500">units</span>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Delayed shipments: <span className="text-slate-200 font-mono">{metrics.delayed_shipments}</span>
        </p>
      </div>

      {/* 5. RESILIENCE SCORE */}
      <div className="p-4 rounded-xl bg-gradient-to-b from-slate-900/90 to-blue-950/30 border border-blue-800/40 glow-blue transition-all">
        <div className="flex items-center justify-between text-xs text-blue-300 mb-1">
          <span className="font-semibold tracking-wide">RESILIENCE SCORE</span>
          <ShieldCheck className="w-4 h-4 text-blue-400" />
        </div>
        <div className="flex items-baseline space-x-1">
          <span className="text-2xl font-bold font-mono text-blue-400">
            {metrics.resilience_score.toFixed(1)}
          </span>
          <span className="text-xs text-slate-400">/ 100</span>
        </div>
        <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-400 transition-all duration-500"
            style={{ width: `${Math.min(100, Math.max(0, metrics.resilience_score))}%` }}
          />
        </div>
      </div>
    </div>
  )
}
