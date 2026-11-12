import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import { Crosshair, Play, TrendingUp, AlertTriangle, ShieldCheck, BarChart3 } from 'lucide-react'

export const StressTestLab: React.FC = () => {
  const [runs, setRuns] = useState<number>(100)
  const [loading, setLoading] = useState<boolean>(false)
  const [summary, setSummary] = useState<any>(null)

  const executeStressTest = async (n: number) => {
    setLoading(true)
    try {
      const data = await api.runStressTest(n)
      setSummary(data.summary)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    executeStressTest(100)
  }, [])

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Crosshair className="w-5 h-5 text-indigo-400" />
            <span>MONTE CARLO STRESS-TESTING LAB</span>
          </h2>
          <p className="text-xs text-slate-400">
            Running 100–1,000 randomized multi-shock simulations to identify worst-case tail risks.
          </p>
        </div>

        {/* Run Selector */}
        <div className="flex items-center space-x-2">
          {[100, 500, 1000].map((n) => (
            <button
              key={n}
              onClick={() => { setRuns(n); executeStressTest(n) }}
              disabled={loading}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                runs === n
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'bg-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {n} Runs
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center bg-slate-900/80 rounded-2xl border border-slate-800 space-y-3">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-300 font-mono">
            Simulating {runs} stochastic disruptions across multi-echelon network...
          </p>
        </div>
      ) : summary ? (
        <>
          {/* Statistical Percentiles Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-slate-400 text-xs block mb-1">EXPECTED SERVICE (MEAN)</span>
              <span className="text-2xl font-bold font-mono text-emerald-400">
                {(summary.mean_service_level * 100).toFixed(1)}%
              </span>
              <span className="text-[11px] text-rose-400 block mt-1">
                Worst-case: {(summary.worst_case_service_level * 100).toFixed(1)}%
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-slate-400 text-xs block mb-1">P90 COST EXPOSURE</span>
              <span className="text-2xl font-bold font-mono text-rose-400">
                ₹{(summary.p90_cost_inr / 100000).toFixed(1)}L
              </span>
              <span className="text-[11px] text-slate-500 block mt-1">
                P50 (Median): ₹{(summary.p50_cost_inr / 100000).toFixed(1)}L
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-slate-400 text-xs block mb-1">P95 RECOVERY TIMELINE</span>
              <span className="text-2xl font-bold font-mono text-amber-400">
                {summary.p95_recovery_days.toFixed(1)} <span className="text-sm font-normal">days</span>
              </span>
              <span className="text-[11px] text-slate-500 block mt-1">
                Mean recovery: {summary.mean_recovery_days.toFixed(1)}d
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-slate-400 text-xs block mb-1">MEAN RESILIENCE SCORE</span>
              <span className="text-2xl font-bold font-mono text-blue-400">
                {summary.mean_resilience_score.toFixed(1)} <span className="text-sm font-normal">/ 100</span>
              </span>
              <span className="text-[11px] text-slate-400 block mt-1">
                {summary.total_scenarios_run} scenarios evaluated
              </span>
            </div>
          </div>

          {/* Loss Distribution Histogram & Top Vulnerable Nodes */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Loss Distribution */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-indigo-400" />
                <span>LOSS DISTRIBUTION SPECTRUM</span>
              </h3>
              <div className="space-y-2 pt-2">
                {summary.loss_distribution_buckets.map((b: any, idx: number) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs text-slate-400">
                      <span>{b.range_inr}</span>
                      <span className="font-mono text-slate-200">{b.frequency} scenarios</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-rose-500 rounded-full"
                        style={{ width: `${(b.frequency / summary.total_scenarios_run) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Most Vulnerable Targets */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>TOP VULNERABILITY BOTTLENECK NODES</span>
              </h3>
              <div className="space-y-2 pt-2">
                {summary.top_vulnerable_targets.map((t: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 flex items-center justify-between text-xs"
                  >
                    <div>
                      <span className="font-bold text-white font-mono">{t.target_id}</span>
                      <span className="text-[11px] text-slate-400 block">{t.runs_evaluated} shock runs</span>
                    </div>
                    <div className="text-right">
                      <span className="font-mono font-bold text-rose-400">
                        -{t.avg_service_loss_pct}%
                      </span>
                      <span className="text-[10px] text-slate-500 block">Avg Service Loss</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  )
}
