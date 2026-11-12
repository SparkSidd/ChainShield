import React from 'react'
import { CascadeLinkItem } from '../types'
import { GitBranch, AlertTriangle, ArrowDown, ShieldAlert, Clock, Layers } from 'lucide-react'

interface CascadeTraceProps {
  cascadeLinks: CascadeLinkItem[]
  isDisrupted: boolean
  onSolveRecovery: () => void
}

export const CascadeTrace: React.FC<CascadeTraceProps> = ({
  cascadeLinks,
  isDisrupted,
  onSolveRecovery
}) => {
  // If no simulation cascade exists yet, provide the primary M#26 canonical Port Strike cascade chain
  const canonicalChain = [
    {
      step: 1,
      time: 'Day 5.0 (00:00)',
      source: 'PORT_JNPT (Navi Mumbai)',
      target: 'PORT_JNPT',
      effect_type: 'PORT_STRIKE_SHOCK',
      headline: 'Terminal Dockworkers Strike Commences',
      magnitude: '-80% Available Port Capacity',
      description: 'Incoming container vessel clearance halted. Terminal gate operations throttled to 20% throughput.',
      severity: 'CRITICAL'
    },
    {
      step: 2,
      time: 'Day 6.5 (12:00)',
      source: 'PORT_JNPT',
      target: 'E_JNPT_PUNE & E_JNPT_MANESAR',
      effect_type: 'QUEUE_BACKLOG',
      headline: 'Container Berth Backlog Escalation',
      magnitude: '+420 Container TEUs Queued',
      description: 'Semiconductor chip consignments stuck in port yards. Feeder road transit delays jump to 4.5 days.',
      severity: 'HIGH'
    },
    {
      step: 3,
      time: 'Day 8.2 (06:00)',
      source: 'FAC_PUNE & FAC_MANESAR',
      target: 'RM_CHIP Buffer',
      effect_type: 'BUFFER_DEPLETION',
      headline: 'Factory Raw Material Inventory Depleted',
      magnitude: '-31% Input Availability',
      description: 'Safety stock of Microcontrollers falls below reorder point (600 units). Time-to-Survive reaches critical zero.',
      severity: 'HIGH'
    },
    {
      step: 4,
      time: 'Day 9.5 (18:00)',
      source: 'FAC_PUNE Assembly Line',
      target: 'FAC_PUNE',
      effect_type: 'PRODUCTION_STARVATION',
      headline: 'Production Throttled & Line Starvation',
      magnitude: '-27% Finished Goods Output',
      description: 'BOM constraint violated: missing RM_CHIP prevents assembly of FG_SMART_IOT and FG_TELECOM_NODE.',
      severity: 'SEVERE'
    },
    {
      step: 5,
      time: 'Day 11.0 (09:00)',
      source: 'WH_MUMBAI (Bhiwandi)',
      target: 'WH_MUMBAI Buffer',
      effect_type: 'STOCKOUT_BREACH',
      headline: 'Warehouse Inventory Falls Below Safety Stock',
      magnitude: '-74% DC Finished Goods Stock',
      description: 'Western distribution center runs out of buffer stock to replenish high-velocity regional retail clusters.',
      severity: 'SEVERE'
    },
    {
      step: 6,
      time: 'Day 13.0 (15:00)',
      source: 'CUST_MUMBAI & CUST_PUNE',
      target: 'End Customer Fulfilment',
      effect_type: 'CUSTOMER_SERVICE_COLLAPSE',
      headline: 'End-Customer Service Level Collapse',
      magnitude: '-14% to -24% Customer Service Drop',
      description: 'Customer order unfulfillment penalties spike to ₹4.5L/day. Lost sales and SLA breach penalties incurred.',
      severity: 'CATASTROPHIC'
    }
  ]

  // If simulation cascade items exist from live SimPy run, use them; otherwise use canonical baseline chain
  const displayChain = cascadeLinks && cascadeLinks.length > 0
    ? cascadeLinks.map((l, idx) => {
        const sev = l.magnitude > 50 || l.effect_type === 'STOCKOUT_BREACH' || l.effect_type === 'CUSTOMER_SERVICE_COLLAPSE'
          ? 'CATASTROPHIC'
          : l.magnitude > 25 || l.effect_type === 'PRODUCTION_STARVATION'
          ? 'SEVERE'
          : 'HIGH'
        return {
          step: idx + 1,
          time: `Day ${l.timestamp.toFixed(1)}`,
          source: l.source_node_or_edge,
          target: l.target_node,
          effect_type: l.effect_type,
          headline: l.cause_description,
          magnitude: `${l.magnitude >= 0 ? '+' : ''}${l.magnitude.toFixed(1)}${l.magnitude_unit || '%'}`,
          description: l.downstream_impact_summary || l.cause_description,
          severity: sev
        }
      })
    : canonicalChain

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-amber-400" />
              <span>CAUSAL CASCADE TRACE: SHOCK PROPAGATION CHAIN</span>
            </h2>
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold ${
              cascadeLinks && cascadeLinks.length > 0
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-slate-800 text-slate-400'
            }`}>
              {cascadeLinks && cascadeLinks.length > 0 ? '● LIVE SIMULATION DAG' : 'CANONICAL CORRIDOR MODEL'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Mapping how an upstream port choke ripples through factory starvation to final customer stockouts.
          </p>
        </div>

        <button
          onClick={onSolveRecovery}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-emerald-600/30 flex items-center gap-2 cursor-pointer"
        >
          <span>Evaluate Recovery Options</span>
        </button>
      </div>

      {/* Causal Step Timeline Cards */}
      <div className="relative pl-6 space-y-4 before:absolute before:left-3 before:top-4 before:bottom-4 before:w-0.5 before:bg-gradient-to-b before:from-rose-500 via-amber-500 to-rose-600">
        {displayChain.map((link, idx) => (
          <div
            key={link.step}
            className="relative bg-slate-900/90 rounded-2xl border border-slate-800 p-5 hover:border-slate-700 transition-all"
          >
            {/* Step circle */}
            <div className="absolute -left-[31px] top-5 w-6 h-6 rounded-full bg-slate-950 border-2 border-amber-400 flex items-center justify-center text-[10px] font-bold text-amber-400">
              {link.step}
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
              <div className="flex items-center space-x-2">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono text-[11px]">
                  {link.time}
                </span>
                <span className="text-xs font-semibold text-white">{link.headline}</span>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                link.severity === 'CATASTROPHIC' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                link.severity === 'SEVERE' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                'bg-amber-500/20 text-amber-300 border border-amber-500/30'
              }`}>
                {link.severity}
              </span>
            </div>

            {/* Impact magnitude callout */}
            <div className="my-2 p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 flex items-center justify-between">
              <span className="text-xs text-slate-400">
                Vector: <span className="text-slate-200 font-mono">{link.source}</span> → <span className="text-slate-200 font-mono">{link.target}</span>
              </span>
              <span className="text-xs font-bold font-mono text-rose-400">
                {link.magnitude}
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {link.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
