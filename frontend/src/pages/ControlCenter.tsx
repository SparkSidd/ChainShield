import React, { useState } from 'react'
import { MetricsReport, NodeItem, EdgeItem, ScreenType } from '../types'
import { MetricCards } from '../components/MetricCards'
import { NetworkMap } from '../components/NetworkMap'
import { Play, RotateCcw, AlertOctagon, ArrowRight, Zap, GitBranch, Layers } from 'lucide-react'

interface ControlCenterProps {
  metrics: MetricsReport | null
  nodes: NodeItem[]
  edges: EdgeItem[]
  isDisrupted: boolean
  onInjectPortStrike: () => void
  onResetBaseline: () => void
  onNavigate: (screen: ScreenType) => void
}

export const ControlCenter: React.FC<ControlCenterProps> = ({
  metrics,
  nodes,
  edges,
  isDisrupted,
  onInjectPortStrike,
  onResetBaseline,
  onNavigate
}) => {
  const [activeDay, setActiveDay] = useState<number>(15)

  return (
    <div className="space-y-6">
      {/* Action Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-blue-950/40 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <span>RESILIENCE LABORATORY CONTROL CENTER</span>
            <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-mono">
              30-DAY HORIZON
            </span>
          </h2>
          <p className="text-xs text-slate-400">
            Simulating multi-echelon industrial electronics supply corridor under stochastic shocks.
          </p>
        </div>

        {/* Demo Trigger Buttons */}
        <div className="flex items-center space-x-3">
          {!isDisrupted ? (
            <button
              onClick={onInjectPortStrike}
              className="flex items-center space-x-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-rose-600/30 transition-all cursor-pointer"
            >
              <AlertOctagon className="w-4 h-4" />
              <span>TRIGGER PORT STRIKE (M#26 DEMO)</span>
            </button>
          ) : (
            <button
              onClick={onResetBaseline}
              className="flex items-center space-x-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700 transition-all cursor-pointer"
            >
              <RotateCcw className="w-4 h-4" />
              <span>RESET BASELINE (NORMAL)</span>
            </button>
          )}

          {isDisrupted && (
            <button
              onClick={() => onNavigate('cascade-trace')}
              className="flex items-center space-x-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-amber-600/30 transition-all cursor-pointer"
            >
              <GitBranch className="w-4 h-4" />
              <span>TRACE CASCADE</span>
            </button>
          )}

          {isDisrupted && (
            <button
              onClick={() => onNavigate('recovery-arena')}
              className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-emerald-600/30 transition-all cursor-pointer"
            >
              <Zap className="w-4 h-4" />
              <span>RECOVERY ARENA</span>
            </button>
          )}
        </div>
      </div>

      {/* Disruption Alert Banner if active */}
      {isDisrupted && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/80 glow-red flex flex-wrap items-center justify-between gap-4 animate-pulse">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold">
              !
            </div>
            <div>
              <h4 className="text-sm font-bold text-rose-300">
                ACTIVE DISRUPTION: JNPT Port Marine Dockworkers Strike
              </h4>
              <p className="text-xs text-slate-300">
                80% capacity choked at JNPT Mumbai • 22 container shipments delayed • Pune & Manesar assembly plants facing raw material starvation.
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <span className="text-rose-300 font-mono font-bold">Service Loss: -24.8%</span>
            <button
              onClick={() => onNavigate('recovery-arena')}
              className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-semibold flex items-center gap-1"
            >
              <span>Solve Recovery</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Top 5 Metrics Cards */}
      <MetricCards metrics={metrics} />

      {/* Interactive Topology Graph */}
      <NetworkMap
        nodes={nodes}
        edges={edges}
        disruptedNodeId={isDisrupted ? 'PORT_JNPT' : null}
      />

      {/* Timeline Controls */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <span className="text-xs font-semibold text-slate-300">SIMULATION TIMELINE</span>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-blue-400 font-mono text-xs">
            Day {activeDay} of 30
          </span>
        </div>

        <div className="flex-1 max-w-xl flex items-center space-x-3">
          <span className="text-xs text-slate-500">Day 1</span>
          <input
            type="range"
            min="1"
            max="30"
            value={activeDay}
            onChange={(e) => setActiveDay(parseInt(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <span className="text-xs text-slate-500">Day 30</span>
        </div>

        <div className="text-xs text-slate-400">
          Status at t={activeDay}d: <span className={isDisrupted && activeDay >= 5 ? 'text-rose-400 font-semibold' : 'text-emerald-400 font-semibold'}>
            {isDisrupted && activeDay >= 5 ? 'PORT SHOCK PROPAGATING' : 'STEADY FLOW'}
          </span>
        </div>
      </div>
    </div>
  )
}
