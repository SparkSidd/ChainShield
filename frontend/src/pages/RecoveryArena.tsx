import React, { useState, useEffect } from 'react'
import { RecoveryArenaComparisonItem, EvaluatedStrategyItem } from '../types'
import { api } from '../services/api'
import { Zap, CheckCircle2, XCircle, Sliders, IndianRupee, Clock, ShieldCheck, ArrowRight, Cpu } from 'lucide-react'

interface RecoveryArenaProps {
  initialDisruptedService?: number
}

export const RecoveryArena: React.FC<RecoveryArenaProps> = ({ initialDisruptedService = 0.74 }) => {
  const [budget, setBudget] = useState<number>(1200000) // ₹12 Lakhs
  const [minService, setMinService] = useState<number>(0.90) // 90%
  const [maxRecoveryDays, setMaxRecoveryDays] = useState<number>(7.0) // 7 days
  const [preference, setPreference] = useState<string>('balanced')
  
  const [comparison, setComparison] = useState<RecoveryArenaComparisonItem | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [mipResult, setMipResult] = useState<any>(null)

  const fetchComparison = async () => {
    setLoading(true)
    try {
      const data = await api.compareRecovery({
        disrupted_target_id: 'PORT_JNPT',
        unfulfilled_demand_units: 600.0,
        disrupted_service_level: initialDisruptedService,
        daily_loss_inr: 450000.0,
        max_budget: budget,
        min_service_level: minService,
        max_recovery_days: maxRecoveryDays,
        preference: preference
      })
      setComparison(data)

      // Also call MIP solver
      const mip = await api.optimizeRecovery({
        max_budget: budget,
        min_service_level: minService,
        max_recovery_days: maxRecoveryDays,
        preference: preference
      })
      setMipResult(mip)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchComparison()
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/30 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-emerald-400" />
            <span>RECOVERY STRATEGY ARENA & MATHEMATICAL OPTIMIZER</span>
          </h2>
          <p className="text-xs text-slate-400">
            Multi-objective trade-off laboratory evaluated under strict operational constraints.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 font-mono border border-emerald-500/30 flex items-center gap-1">
            <Cpu className="w-3.5 h-3.5" />
            HiGHS MIP SOLVER ACTIVE
          </span>
        </div>
      </div>

      {/* Constraints Control Panel */}
      <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
        <h3 className="text-xs font-bold text-slate-300 tracking-wider flex items-center gap-2">
          <Sliders className="w-4 h-4 text-blue-400" />
          <span>SET OPERATIONAL CONSTRAINTS & PREFERENCES</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Budget */}
          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
            <label className="text-xs text-slate-400 block mb-1">
              MAX ADDITIONAL BUDGET: <span className="text-white font-mono font-bold">₹{(budget / 100000).toFixed(1)}L</span>
            </label>
            <input
              type="range"
              min="200000"
              max="2500000"
              step="50000"
              value={budget}
              onChange={(e) => setBudget(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>₹2L</span>
              <span>₹25L</span>
            </div>
          </div>

          {/* Min Service */}
          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
            <label className="text-xs text-slate-400 block mb-1">
              MIN SERVICE LEVEL: <span className="text-white font-mono font-bold">{(minService * 100).toFixed(0)}%</span>
            </label>
            <input
              type="range"
              min="0.75"
              max="0.98"
              step="0.01"
              value={minService}
              onChange={(e) => setMinService(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>75%</span>
              <span>98%</span>
            </div>
          </div>

          {/* Max Recovery Days */}
          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
            <label className="text-xs text-slate-400 block mb-1">
              MAX RECOVERY DEADLINE: <span className="text-white font-mono font-bold">{maxRecoveryDays.toFixed(1)}d</span>
            </label>
            <input
              type="range"
              min="2"
              max="14"
              step="0.5"
              value={maxRecoveryDays}
              onChange={(e) => setMaxRecoveryDays(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>2 days</span>
              <span>14 days</span>
            </div>
          </div>

          {/* Objective Preference */}
          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 flex flex-col justify-between">
            <label className="text-xs text-slate-400 block mb-1">OPTIMIZER FOCUS</label>
            <select
              value={preference}
              onChange={(e) => setPreference(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg text-xs p-1.5 text-white"
            >
              <option value="balanced">Balanced (Cost + Service + Time)</option>
              <option value="cost_first">Cost-First (Minimize spend)</option>
              <option value="service_first">Service-First (Maximize fulfillment)</option>
              <option value="recovery_first">Speed-First (Fastest recovery)</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end pt-1">
          <button
            onClick={fetchComparison}
            disabled={loading}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/30 transition-all cursor-pointer flex items-center gap-2"
          >
            <Zap className="w-4 h-4" />
            <span>{loading ? 'SOLVING MIP...' : 'RERUN OPTIMIZATION'}</span>
          </button>
        </div>
      </div>

      {/* Side-by-Side Comparison Table */}
      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-white">
            STRATEGY TRADE-OFF MATRIX & PARETO FRONTIER
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">RECOVERY STRATEGY</th>
                <th className="px-4 py-3">INCREMENTAL COST</th>
                <th className="px-4 py-3">RECOVERY TIME</th>
                <th className="px-4 py-3">SERVICE LEVEL</th>
                <th className="px-4 py-3">STOCKOUT REDUCTION</th>
                <th className="px-4 py-3">PARETO OPTIMAL</th>
                <th className="px-4 py-3">FEASIBILITY</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {comparison?.strategies.map((strat) => {
                const isRecommended = comparison.best_feasible_strategy?.strategy_id === strat.strategy_id
                const pareto = comparison.pareto_frontier.find((p) => p.strategy_id === strat.strategy_id)

                return (
                  <tr
                    key={strat.strategy_id}
                    className={`transition-colors ${
                      isRecommended ? 'bg-emerald-950/30 font-semibold' : 'hover:bg-slate-800/40'
                    }`}
                  >
                    <td className="px-4 py-3 font-sans">
                      <div className="flex items-center space-x-2">
                        {isRecommended && (
                          <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold border border-emerald-500/30">
                            BEST
                          </span>
                        )}
                        <span className="text-white font-medium">{strat.name}</span>
                      </div>
                      <p className="text-[11px] text-slate-400 font-sans mt-0.5">{strat.description}</p>
                    </td>
                    <td className="px-4 py-3 text-white">
                      ₹{(strat.incremental_cost_inr / 100000).toFixed(1)}L
                    </td>
                    <td className="px-4 py-3 text-amber-300">
                      {strat.expected_recovery_days.toFixed(1)} days
                    </td>
                    <td className="px-4 py-3 text-emerald-400">
                      {(strat.expected_service_level * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {strat.stockout_reduction_units} units
                    </td>
                    <td className="px-4 py-3">
                      {pareto?.is_pareto_optimal ? (
                        <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 text-[10px] font-sans border border-blue-500/30">
                          Non-Dominated
                        </span>
                      ) : (
                        <span className="text-slate-500 font-sans text-[11px]">Dominated</span>
                      )}
                    </td>
                    <td className="px-4 py-3 font-sans">
                      {strat.feasible ? (
                        <span className="flex items-center text-emerald-400 gap-1 font-semibold">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          FEASIBLE
                        </span>
                      ) : (
                        <div className="text-rose-400 text-[11px]">
                          <span className="flex items-center gap-1 font-semibold">
                            <XCircle className="w-3.5 h-3.5" />
                            INVALID
                          </span>
                          <span className="text-slate-500 text-[10px] block truncate max-w-xs">
                            {strat.infeasibility_reasons[0]}
                          </span>
                        </div>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Executive Decision Rationale */}
      {comparison && (
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h4 className="text-xs font-bold text-slate-300 tracking-wider uppercase mb-1">
              MATHEMATICAL OPTIMIZER VERDICT (EXPLAINABLE OR)
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed max-w-4xl">
              {comparison.executive_recommendation}
            </p>
          </div>
          {mipResult?.status === 'OPTIMAL' && (
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono">
              <span className="text-slate-400 block text-[10px]">HiGHS OBJECTIVE VALUE</span>
              <span className="text-blue-400 font-bold">{mipResult.objective_value.toLocaleString()}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
