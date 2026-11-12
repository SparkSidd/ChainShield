import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import { ShieldAlert, Crosshair, AlertTriangle, Layers, ArrowRight } from 'lucide-react'

export const CriticalityRankings: React.FC = () => {
  const [report, setReport] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'ports' | 'suppliers' | 'factories' | 'routes'>('ports')

  useEffect(() => {
    api.getCriticality().then(setReport).catch(console.error)
  }, [])

  if (!report) {
    return (
      <div className="p-12 text-center text-slate-400">
        <div className="w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-xs font-mono">Evaluating node failure knockouts across multi-echelon graph...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-orange-950/30 border border-slate-800">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-orange-400" />
          <span>SYSTEMIC CRITICALITY & FAILURE MODE ANALYSIS</span>
        </h2>
        <p className="text-xs text-slate-400">
          Rankings derived from simulated knockout experiments and graph topological centrality.
        </p>
      </div>

      {/* Failure Mode Comparison (Random vs Targeted) */}
      <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Crosshair className="w-4 h-4 text-rose-400" />
          <span>FAILURE MODE IMPACT BENCHMARK: NOT ALL DISRUPTIONS ARE EQUAL</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {report.failure_mode_comparison.map((f: any) => (
            <div
              key={f.mode}
              className={`p-4 rounded-xl border flex flex-col justify-between ${
                f.mode === 'TARGETED_CRITICAL_FAILURE'
                  ? 'bg-rose-950/30 border-rose-800/80 glow-red'
                  : 'bg-slate-950/60 border-slate-800'
              }`}
            >
              <div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {f.mode.replace('_', ' ')}
                </span>
                <h4 className="text-xs font-bold text-white mt-2 mb-1 truncate">{f.target_node_name}</h4>
                <p className="text-[11px] text-slate-400 font-sans leading-tight mb-2">
                  Severity: <span className={f.mode === 'TARGETED_CRITICAL_FAILURE' ? 'text-rose-400 font-bold' : 'text-slate-300'}>{f.impact_severity}</span>
                </p>
              </div>

              <div className="pt-2 border-t border-slate-800/80">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">Service Loss:</span>
                  <span className="text-rose-400 font-bold">-{f.service_loss_pct}%</span>
                </div>
                <div className="flex justify-between text-xs font-mono mt-1">
                  <span className="text-slate-400">Cost:</span>
                  <span className="text-slate-200">₹{(f.total_cost_inr / 100000).toFixed(1)}L</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Criticality Entity Tabs */}
      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {[
              { id: 'ports', label: 'Ports' },
              { id: 'suppliers', label: 'Suppliers' },
              { id: 'factories', label: 'Factories' },
              { id: 'routes', label: 'Critical Routes' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white font-semibold'
                    : 'text-slate-400 hover:text-white bg-slate-800/60'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {activeTab === 'ports' ? `${report.most_critical_ports.length} Nodes` : ''}
          </span>
        </div>

        <div className="p-4 space-y-3">
          {(activeTab === 'ports' ? report.most_critical_ports :
            activeTab === 'suppliers' ? report.most_critical_suppliers :
            activeTab === 'factories' ? report.most_critical_factories :
            report.most_critical_routes).map((item: any) => (
            <div
              key={item.id}
              className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="max-w-xl">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-bold text-white text-sm">{item.name}</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {item.id}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{item.why_critical}</p>
                <span className="text-[11px] text-amber-400 block mt-1">
                  Vulnerability: {item.failure_mode_vulnerability}
                </span>
              </div>

              <div className="flex items-center space-x-6 text-xs font-mono">
                <div>
                  <span className="text-slate-500 block text-[10px]">DOWNSTREAM DEMAND</span>
                  <span className="text-slate-200 font-bold">{item.downstream_dependent_demand_pct}%</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">CRITICALITY SCORE</span>
                  <span className="text-2xl font-bold text-amber-400">{item.criticality_score}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
