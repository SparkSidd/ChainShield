import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import { Cpu, CheckCircle2, TrendingUp, ShieldCheck, ArrowRight, GitCommit } from 'lucide-react'

export const NetworkRedesign: React.FC = () => {
  const [addSupplier, setAddSupplier] = useState<boolean>(true)
  const [addRailBypass, setAddRailBypass] = useState<boolean>(true)
  const [addMundra, setAddMundra] = useState<boolean>(true)
  const [bufferPct, setBufferPct] = useState<number>(40)
  const [loading, setLoading] = useState<boolean>(false)
  const [data, setData] = useState<any>(null)

  const evaluateRedesign = async () => {
    setLoading(true)
    try {
      const res = await api.evaluateRedesign({
        add_backup_chip_supplier: addSupplier,
        diversify_sourcing_allocation: true,
        add_freight_corridor_bypass: addRailBypass,
        increase_safety_stock_pct: bufferPct,
        add_mundra_alternate_port: addMundra
      })
      setData(res)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    evaluateRedesign()
  }, [])

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-teal-950/40 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-teal-400" />
            <span>PROACTIVE NETWORK REDESIGN & TOPOLOGICAL HARDENING</span>
          </h2>
          <p className="text-xs text-slate-400">
            Re-architect supply chain topology, eliminate single points of failure, and benchmark resilience gains.
          </p>
        </div>

        <button
          onClick={evaluateRedesign}
          disabled={loading}
          className="px-5 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-teal-600/30 transition-all cursor-pointer flex items-center gap-2"
        >
          <TrendingUp className="w-4 h-4" />
          <span>{loading ? 'EVALUATING STRESS GAINS...' : 'BENCHMARK REDESIGNED TOPOLOGY'}</span>
        </button>
      </div>

      {/* Redesign Levers */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-5 rounded-2xl bg-slate-900/90 border border-slate-800">
        <label className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 flex items-start space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={addSupplier}
            onChange={(e) => setAddSupplier(e.target.checked)}
            className="mt-1 accent-teal-500 rounded"
          />
          <div>
            <span className="text-xs font-bold text-white block">Domestic Chip Foundry</span>
            <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
              Hyderabad Semiconductor dual-sourcing for Pune plant.
            </p>
          </div>
        </label>

        <label className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 flex items-start space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={addMundra}
            onChange={(e) => setAddMundra(e.target.checked)}
            className="mt-1 accent-teal-500 rounded"
          />
          <div>
            <span className="text-xs font-bold text-white block">Mundra Alternate Port</span>
            <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
              Secondary gateway relieving 68% JNPT volume choke.
            </p>
          </div>
        </label>

        <label className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 flex items-start space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={addRailBypass}
            onChange={(e) => setAddRailBypass(e.target.checked)}
            className="mt-1 accent-teal-500 rounded"
          />
          <div>
            <span className="text-xs font-bold text-white block">DFCC Rail Freight Bypass</span>
            <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
              Direct Pune to Gurgaon rail corridor link.
            </p>
          </div>
        </label>

        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
          <label className="text-xs text-slate-400 block mb-1">
            STRATEGIC BUFFER EXPANSION: <span className="text-teal-400 font-mono font-bold">+{bufferPct}%</span>
          </label>
          <input
            type="range"
            min="0"
            max="100"
            step="10"
            value={bufferPct}
            onChange={(e) => setBufferPct(parseInt(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-teal-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-1">
            <span>0%</span>
            <span>+100%</span>
          </div>
        </div>
      </div>

      {/* Criticality Shifts & Resilience Gain */}
      {data && (
        <div className="space-y-6">
          {/* Top Gains Banner */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 block mb-1">SERVICE RETENTION GAIN</span>
              <span className="text-2xl font-bold font-mono text-emerald-400">
                +{data.service_retention_gain_pct}%
              </span>
              <p className="text-[11px] text-slate-400 mt-1">Across randomized disruptions</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 block mb-1">P95 RECOVERY REDUCTION</span>
              <span className="text-2xl font-bold font-mono text-teal-300">
                -{data.p95_recovery_reduction_days} <span className="text-sm font-normal">days</span>
              </span>
              <p className="text-[11px] text-slate-400 mt-1">Faster restoration timeline</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 block mb-1">RESILIENCE SCORE LIFT</span>
              <span className="text-2xl font-bold font-mono text-blue-400">
                +{data.resilience_score_improvement} <span className="text-sm font-normal">pts</span>
              </span>
              <p className="text-[11px] text-slate-400 mt-1">Composite lab score jump</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 block mb-1">LEVERS APPLIED</span>
              <span className="text-2xl font-bold font-mono text-white">
                {data.structural_changes_applied.length}
              </span>
              <p className="text-[11px] text-slate-400 mt-1">Architectural modifications</p>
            </div>
          </div>

          {/* Criticality Shift Cards */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              CRITICALITY EXPOSURE REDUCTIONS (BEFORE VS. AFTER REDESIGN)
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {data.criticality_shifts.map((shift: any, idx: number) => (
                <div key={idx} className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">{shift.name}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold">
                      {shift.change > 0 ? '+' : ''}{shift.change}
                    </span>
                  </div>

                  <div className="flex items-center justify-between font-mono text-xs">
                    <div>
                      <span className="text-slate-500 block text-[10px]">BEFORE</span>
                      <span className="text-rose-400 font-bold text-lg">{shift.before_score}</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-600" />
                    <div>
                      <span className="text-slate-500 block text-[10px]">AFTER</span>
                      <span className="text-emerald-400 font-bold text-lg">{shift.after_score}</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-400 leading-tight">
                    {shift.rationale}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Engineering Verdict */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
            <h4 className="text-xs font-bold text-teal-400 uppercase tracking-wider mb-1">
              ENGINEERING VERDICT
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              {data.engineering_verdict}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
