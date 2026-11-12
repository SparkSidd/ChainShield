import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import { Sliders, Play, TrendingUp, TrendingDown, IndianRupee, Clock, ShieldAlert } from 'lucide-react'

export const WhatIfExplorer: React.FC = () => {
  const [demandSurge, setDemandSurge] = useState<number>(30) // +30%
  const [portCapacity, setPortCapacity] = useState<number>(20) // 20% available (-80% strike)
  const [duration, setDuration] = useState<number>(8) // 8 days
  const [bufferMultiplier, setBufferMultiplier] = useState<number>(1.0)
  const [loading, setLoading] = useState<boolean>(false)
  const [result, setResult] = useState<any>(null)

  const runScenario = async () => {
    setLoading(true)
    try {
      const data = await api.runWhatIf({
        scenario_name: `Surge +${demandSurge}% & Port Capacity ${portCapacity}%`,
        demand_multiplier: 1.0 + (demandSurge / 100.0),
        port_capacity_multiplier: portCapacity / 100.0,
        inventory_buffer_multiplier: bufferMultiplier,
        disruption_duration_days: duration,
        horizon_days: 25,
        seed: 42
      })
      setResult(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    runScenario()
  }, [])

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-sky-950/40 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-sky-400" />
            <span>WHAT-IF SENSITIVITY EXPLORER</span>
          </h2>
          <p className="text-xs text-slate-400">
            Interactive parameter sandbox testing counterfactual operational shocks against immutable baseline.
          </p>
        </div>

        <button
          onClick={runScenario}
          disabled={loading}
          className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/30 transition-all cursor-pointer flex items-center gap-2"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>{loading ? 'RUNNING SIMULATION...' : 'EXECUTE WHAT-IF SCENARIO'}</span>
        </button>
      </div>

      {/* Sliders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-5 rounded-2xl bg-slate-900/90 border border-slate-800">
        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
          <label className="text-xs text-slate-400 block mb-1">
            DEMAND SURGE: <span className="text-emerald-400 font-mono font-bold">+{demandSurge}%</span>
          </label>
          <input
            type="range"
            min="0"
            max="150"
            step="10"
            value={demandSurge}
            onChange={(e) => setDemandSurge(parseInt(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-1">
            <span>0% (Normal)</span>
            <span>+150%</span>
          </div>
        </div>

        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
          <label className="text-xs text-slate-400 block mb-1">
            PORT CAPACITY: <span className="text-rose-400 font-mono font-bold">{portCapacity}%</span>
          </label>
          <input
            type="range"
            min="0"
            max="100"
            step="10"
            value={portCapacity}
            onChange={(e) => setPortCapacity(parseInt(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-rose-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-1">
            <span>0% (Blocked)</span>
            <span>100% (Normal)</span>
          </div>
        </div>

        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
          <label className="text-xs text-slate-400 block mb-1">
            DISRUPTION DURATION: <span className="text-amber-300 font-mono font-bold">{duration} days</span>
          </label>
          <input
            type="range"
            min="1"
            max="20"
            step="1"
            value={duration}
            onChange={(e) => setDuration(parseInt(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-1">
            <span>1 day</span>
            <span>20 days</span>
          </div>
        </div>

        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
          <label className="text-xs text-slate-400 block mb-1">
            INVENTORY BUFFER MULTIPLIER: <span className="text-blue-400 font-mono font-bold">{bufferMultiplier.toFixed(1)}x</span>
          </label>
          <input
            type="range"
            min="0.5"
            max="2.0"
            step="0.1"
            value={bufferMultiplier}
            onChange={(e) => setBufferMultiplier(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-1">
            <span>0.5x</span>
            <span>2.0x</span>
          </div>
        </div>
      </div>

      {/* Comparison Diff Results */}
      {result && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Service Level */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 block mb-1 font-semibold">SERVICE LEVEL</span>
              <div className="flex items-baseline justify-between">
                <div>
                  <span className="text-xs text-slate-500">Base: </span>
                  <span className="text-sm font-mono text-slate-300 font-bold">
                    {(result.baseline_metrics.service_level * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-500">What-If: </span>
                  <span className={`text-xl font-mono font-bold ${
                    result.whatif_metrics.service_level >= 0.90 ? 'text-emerald-400' : 'text-rose-400'
                  }`}>
                    {(result.whatif_metrics.service_level * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              <span className={`text-xs font-mono font-semibold block mt-2 ${
                result.comparisons.service_level.absolute_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'
              }`}>
                Delta: {(result.comparisons.service_level.absolute_delta * 100).toFixed(1)}%
              </span>
            </div>

            {/* Total Cost */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 block mb-1 font-semibold">OPERATING COST</span>
              <div className="flex items-baseline justify-between">
                <div>
                  <span className="text-xs text-slate-500">Base: </span>
                  <span className="text-sm font-mono text-slate-300 font-bold">
                    ₹{(result.baseline_metrics.total_transport_cost / 100000).toFixed(1)}L
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-500">What-If: </span>
                  <span className="text-xl font-mono font-bold text-white">
                    ₹{(result.whatif_metrics.total_transport_cost / 100000).toFixed(1)}L
                  </span>
                </div>
              </div>
              <span className="text-xs font-mono text-rose-400 font-semibold block mt-2">
                Cost Change: {result.comparisons.total_cost_inr.percentage_change > 0 ? '+' : ''}
                {result.comparisons.total_cost_inr.percentage_change.toFixed(1)}%
              </span>
            </div>

            {/* Delayed Shipments */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 block mb-1 font-semibold">DELAYED SHIPMENTS</span>
              <div className="flex items-baseline justify-between">
                <div>
                  <span className="text-xs text-slate-500">Base: </span>
                  <span className="text-sm font-mono text-slate-300 font-bold">
                    {result.baseline_metrics.delayed_shipments}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-500">What-If: </span>
                  <span className="text-xl font-mono font-bold text-amber-400">
                    {result.whatif_metrics.delayed_shipments}
                  </span>
                </div>
              </div>
              <span className="text-xs font-mono text-slate-400 block mt-2">
                Avg delay: {result.whatif_metrics.avg_shipment_delay_days.toFixed(1)} days
              </span>
            </div>

            {/* Resilience Score */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 block mb-1 font-semibold">RESILIENCE SCORE</span>
              <div className="flex items-baseline justify-between">
                <div>
                  <span className="text-xs text-slate-500">Base: </span>
                  <span className="text-sm font-mono text-slate-300 font-bold">
                    {result.baseline_metrics.resilience_score.toFixed(1)}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-500">What-If: </span>
                  <span className="text-xl font-mono font-bold text-blue-400">
                    {result.whatif_metrics.resilience_score.toFixed(1)}
                  </span>
                </div>
              </div>
              <span className={`text-xs font-mono font-semibold block mt-2 ${
                result.comparisons.resilience_score.absolute_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'
              }`}>
                Score Shift: {result.comparisons.resilience_score.absolute_delta > 0 ? '+' : ''}
                {result.comparisons.resilience_score.absolute_delta.toFixed(1)}
              </span>
            </div>
          </div>

          {/* Narrative Executive Insight */}
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
              SCENARIO IMPACT SUMMARY
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              {result.executive_insight}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
