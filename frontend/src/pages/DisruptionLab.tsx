import React, { useState } from 'react'
import { Flame, ShieldAlert, Truck, Anchor, Clock, TrendingUp, Check } from 'lucide-react'

interface DisruptionLabProps {
  onTriggerDisruption: (disr: any) => void
}

export const DisruptionLab: React.FC<DisruptionLabProps> = ({ onTriggerDisruption }) => {
  const [disrType, setDisrType] = useState<string>('PORT_STRIKE')
  const [targetId, setTargetId] = useState<string>('PORT_JNPT')
  const [duration, setDuration] = useState<number>(10)
  const [severity, setSeverity] = useState<number>(80) // 80% loss
  const [triggered, setTriggered] = useState<boolean>(false)

  const handleLaunch = () => {
    onTriggerDisruption({
      id: `DISR_LAB_${Date.now()}`,
      name: `Custom Shock: ${targetId}`,
      disruption_type: disrType,
      target_id: targetId,
      start_day: 5.0,
      duration_days: duration,
      capacity_multiplier: Math.max(0.0, (100 - severity) / 100),
      delay_multiplier: 1.0 + (severity / 50.0)
    })
    setTriggered(true)
    setTimeout(() => setTriggered(false), 3000)
  }

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Flame className="w-5 h-5 text-rose-400" />
          <span>DISRUPTION INJECTION LAB (M#26 CORE SCENARIOS)</span>
        </h2>
        <p className="text-xs text-slate-400">
          Inject real-world operational breakdowns and observe system-wide causal cascades.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Scenario Selector */}
        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            1. SELECT DISRUPTION TYPE
          </h3>

          <div className="grid grid-cols-2 gap-3">
            {[
              { id: 'PORT_STRIKE', label: 'Port Strike', icon: <Anchor className="w-4 h-4 text-sky-400" />, desc: 'Throttles container clearance & berthing.' },
              { id: 'VEHICLE_BREAKDOWN', label: 'Vehicle Breakdown', icon: <Truck className="w-4 h-4 text-amber-400" />, desc: 'Transit route capacity loss & lead time surge.' },
              { id: 'SHIPMENT_DELAY', label: 'Shipment Delay', icon: <Clock className="w-4 h-4 text-rose-400" />, desc: 'Transit corridor congestion & buffer depletion.' },
              { id: 'DEMAND_SURGE', label: 'Demand Surge', icon: <TrendingUp className="w-4 h-4 text-emerald-400" />, desc: 'Sudden +40% to +80% customer order spike.' },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setDisrType(item.id)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  disrType === item.id
                    ? 'bg-blue-600/20 border-blue-500 text-white'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center space-x-2 mb-1">
                  {item.icon}
                  <span className="font-semibold text-xs text-white">{item.label}</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-tight">{item.desc}</p>
              </button>
            ))}
          </div>

          <div className="space-y-3 pt-2">
            <div>
              <label className="text-xs text-slate-400 block mb-1">TARGET CORRIDOR / FACILITY</label>
              <select
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg text-xs p-2 text-white"
              >
                <option value="PORT_JNPT">PORT_JNPT (JNPT Port Mumbai - 68% volume)</option>
                <option value="PORT_CHENNAI">PORT_CHENNAI (Chennai Port Marine Hub - 32% volume)</option>
                <option value="E_JNPT_PUNE">E_JNPT_PUNE (Expressway Container Link)</option>
                <option value="SUP_TAIWAN_SEMICON">SUP_TAIWAN_SEMICON (Sole Source Microchips)</option>
                <option value="FAC_PUNE">FAC_PUNE (Pune Mega Electronics Assembly)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Shock Parameters */}
        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div className="space-y-4">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              2. SHOCK MAGNITUDE & TIMELINE
            </h3>

            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>SEVERITY (CAPACITY LOSS):</span>
                <span className="text-rose-400 font-mono font-bold">-{severity}%</span>
              </div>
              <input
                type="range"
                min="10"
                max="100"
                step="5"
                value={severity}
                onChange={(e) => setSeverity(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-rose-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>SHOCK DURATION:</span>
                <span className="text-amber-300 font-mono font-bold">{duration} days</span>
              </div>
              <input
                type="range"
                min="2"
                max="25"
                step="1"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
            </div>
          </div>

          <button
            onClick={handleLaunch}
            className="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-rose-600/30 transition-all cursor-pointer flex items-center justify-center gap-2"
          >
            {triggered ? (
              <>
                <Check className="w-4 h-4 text-white" />
                <span>SHOCK INJECTED INTO SIMULATION!</span>
              </>
            ) : (
              <>
                <Flame className="w-4 h-4 text-white" />
                <span>INJECT DISRUPTION INTO NETWORK</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
