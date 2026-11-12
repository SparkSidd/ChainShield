import React from 'react'
import { ScreenType } from '../types'
import { 
  ShieldAlert, 
  Activity, 
  Network, 
  GitBranch, 
  Crosshair, 
  Zap, 
  Sliders, 
  Cpu, 
  Flame,
  CheckCircle2
} from 'lucide-react'

interface NavbarProps {
  currentScreen: ScreenType
  onSelectScreen: (screen: ScreenType) => void
  isDisrupted: boolean
}

export const Navbar: React.FC<NavbarProps> = ({ currentScreen, onSelectScreen, isDisrupted }) => {
  const tabs: { id: ScreenType; label: string; icon: React.ReactNode }[] = [
    { id: 'control-center', label: 'Control Center', icon: <Activity className="w-4 h-4" /> },
    { id: 'network', label: 'Network', icon: <Network className="w-4 h-4" /> },
    { id: 'disruption-lab', label: 'Disruption Lab', icon: <Flame className="w-4 h-4 text-rose-400" /> },
    { id: 'cascade-trace', label: 'Cascade Trace', icon: <GitBranch className="w-4 h-4 text-amber-400" /> },
    { id: 'recovery-arena', label: 'Recovery Arena', icon: <Zap className="w-4 h-4 text-emerald-400" /> },
    { id: 'stress-test', label: 'Stress Test', icon: <Crosshair className="w-4 h-4 text-indigo-400" /> },
    { id: 'criticality', label: 'Criticality', icon: <ShieldAlert className="w-4 h-4 text-orange-400" /> },
    { id: 'what-if', label: 'What-If Explorer', icon: <Sliders className="w-4 h-4 text-sky-400" /> },
    { id: 'redesign', label: 'Network Redesign', icon: <Cpu className="w-4 h-4 text-teal-400" /> },
  ]

  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-wider text-white">CHAINSHIELD</span>
              <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-mono border border-blue-500/30">M#26 PS#10</span>
              {isDisrupted ? (
                <span className="text-xs px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-semibold border border-rose-500/30 animate-pulse flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                  SHOCK ACTIVE
                </span>
              ) : (
                <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-medium border border-emerald-500/30 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  NORMAL
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 font-light">
              Dynamic Supply Chain Recovery & Resilience Simulator
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800/80 overflow-x-auto">
          {tabs.map((tab) => {
            const isActive = currentScreen === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => onSelectScreen(tab.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
