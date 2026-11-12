import React, { useState, useEffect } from 'react'
import { ScreenType, MetricsReport, NodeItem, EdgeItem, CascadeLinkItem } from './types'
import { api } from './services/api'
import { Navbar } from './components/Navbar'
import { ControlCenter } from './pages/ControlCenter'
import { NetworkView } from './pages/NetworkView'
import { DisruptionLab } from './pages/DisruptionLab'
import { CascadeTrace } from './pages/CascadeTrace'
import { RecoveryArena } from './pages/RecoveryArena'
import { StressTestLab } from './pages/StressTestLab'
import { CriticalityRankings } from './pages/CriticalityRankings'
import { WhatIfExplorer } from './pages/WhatIfExplorer'
import { NetworkRedesign } from './pages/NetworkRedesign'

export const App: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<ScreenType>('control-center')
  const [nodes, setNodes] = useState<NodeItem[]>([])
  const [edges, setEdges] = useState<EdgeItem[]>([])
  const [metrics, setMetrics] = useState<MetricsReport | null>(null)
  const [cascadeLinks, setCascadeLinks] = useState<CascadeLinkItem[]>([])
  const [isDisrupted, setIsDisrupted] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(true)

  // Initialize network & run healthy baseline simulation on startup
  const initApp = async () => {
    setLoading(true)
    try {
      const net = await api.getNetwork()
      setNodes(net.nodes)
      setEdges(net.edges)

      // Run baseline healthy 30-day simulation
      const sim = await api.runSimulation({ horizon_days: 30, seed: 42 })
      setMetrics(sim.metrics)
      setIsDisrupted(false)
    } catch (err) {
      console.error('Initialization error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    initApp()
  }, [])

  // Primary M#26 Demo: Trigger Port Strike Disruption at JNPT
  const handleInjectPortStrike = async () => {
    setLoading(true)
    try {
      const sim = await api.runSimulation({
        horizon_days: 30,
        seed: 42,
        disruptions: [
          {
            id: 'DISR_PORT_STRIKE_JNPT',
            name: 'JNPT Port Marine Terminal Strike',
            disruption_type: 'PORT_STRIKE',
            target_id: 'PORT_JNPT',
            start_day: 5.0,
            duration_days: 10.0,
            capacity_multiplier: 0.20,
            delay_multiplier: 2.5
          }
        ]
      })
      setMetrics(sim.metrics)
      if (sim.cascade?.chain && sim.cascade.chain.length > 0) {
        setCascadeLinks(sim.cascade.chain)
      }
      setIsDisrupted(true)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Reset to Healthy Baseline
  const handleResetBaseline = async () => {
    setLoading(true)
    try {
      const sim = await api.runSimulation({ horizon_days: 30, seed: 42, disruptions: [] })
      setMetrics(sim.metrics)
      setIsDisrupted(false)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        currentScreen={currentScreen}
        onSelectScreen={setCurrentScreen}
        isDisrupted={isDisrupted}
      />

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        {currentScreen === 'control-center' && (
          <ControlCenter
            metrics={metrics}
            nodes={nodes}
            edges={edges}
            isDisrupted={isDisrupted}
            onInjectPortStrike={handleInjectPortStrike}
            onResetBaseline={handleResetBaseline}
            onNavigate={setCurrentScreen}
          />
        )}

        {currentScreen === 'network' && (
          <NetworkView nodes={nodes} edges={edges} />
        )}

        {currentScreen === 'disruption-lab' && (
          <DisruptionLab
            onTriggerDisruption={(disr) => {
              api.runSimulation({ horizon_days: 30, seed: 42, disruptions: [disr] }).then((res) => {
                setMetrics(res.metrics)
                if (res.cascade?.chain && res.cascade.chain.length > 0) {
                  setCascadeLinks(res.cascade.chain)
                }
                setIsDisrupted(true)
                setCurrentScreen('control-center')
              })
            }}
          />
        )}

        {currentScreen === 'cascade-trace' && (
          <CascadeTrace
            cascadeLinks={cascadeLinks}
            isDisrupted={isDisrupted}
            onSolveRecovery={() => setCurrentScreen('recovery-arena')}
          />
        )}

        {currentScreen === 'recovery-arena' && (
          <RecoveryArena
            initialDisruptedService={metrics?.service_level || 0.74}
          />
        )}

        {currentScreen === 'stress-test' && (
          <StressTestLab />
        )}

        {currentScreen === 'criticality' && (
          <CriticalityRankings />
        )}

        {currentScreen === 'what-if' && (
          <WhatIfExplorer />
        )}

        {currentScreen === 'redesign' && (
          <NetworkRedesign />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-4 text-center text-xs text-slate-400">
        <p>
          CHAINSHIELD • Manipal Hackathon 2026 (M#26 PS #10) • Discrete-Event SimPy Engine + Pyomo/HiGHS MIP Optimizer
        </p>
      </footer>
    </div>
  )
}

export default App
