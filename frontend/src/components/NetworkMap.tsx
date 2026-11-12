import React, { useState } from 'react'
import { NodeItem, EdgeItem } from '../types'
import { Anchor, Factory, Warehouse, Users, Cpu, AlertCircle, CheckCircle, Info } from 'lucide-react'

interface NetworkMapProps {
  nodes: NodeItem[]
  edges: EdgeItem[]
  disruptedNodeId?: string | null
  disruptedEdgeId?: string | null
}

export const NetworkMap: React.FC<NetworkMapProps> = ({
  nodes,
  edges,
  disruptedNodeId,
  disruptedEdgeId
}) => {
  const [selectedNode, setSelectedNode] = useState<NodeItem | null>(null)

  // Layout nodes into 5 horizontal echelons across SVG canvas (width 1000, height 520)
  // Echelon 1: Suppliers (x: 100)
  // Echelon 2: Ports (x: 280)
  // Echelon 3: Factories (x: 480)
  // Echelon 4: Warehouses (x: 680)
  // Echelon 5: Customers (x: 880)
  const getNodeCoordinates = (node: NodeItem, index: number, totalInType: number) => {
    let x = 500
    if (node.type === 'SUPPLIER') x = 90
    else if (node.type === 'PORT') x = 270
    else if (node.type === 'FACTORY') x = 470
    else if (node.type === 'WAREHOUSE') x = 680
    else if (node.type === 'CUSTOMER') x = 890

    // Distribute y evenly along height
    const paddingY = 60
    const availableHeight = 420
    const step = totalInType > 1 ? availableHeight / (totalInType - 1) : availableHeight / 2
    const y = paddingY + index * step

    return { x, y }
  }

  // Group nodes by type for layout indexing
  const suppliers = nodes.filter((n) => n.type === 'SUPPLIER')
  const ports = nodes.filter((n) => n.type === 'PORT')
  const factories = nodes.filter((n) => n.type === 'FACTORY')
  const warehouses = nodes.filter((n) => n.type === 'WAREHOUSE')
  const customers = nodes.filter((n) => n.type === 'CUSTOMER')

  const nodePosMap: Record<string, { x: number; y: number }> = {}

  suppliers.forEach((n, i) => { nodePosMap[n.id] = getNodeCoordinates(n, i, suppliers.length) })
  ports.forEach((n, i) => { nodePosMap[n.id] = getNodeCoordinates(n, i, ports.length) })
  factories.forEach((n, i) => { nodePosMap[n.id] = getNodeCoordinates(n, i, factories.length) })
  warehouses.forEach((n, i) => { nodePosMap[n.id] = getNodeCoordinates(n, i, warehouses.length) })
  customers.forEach((n, i) => { nodePosMap[n.id] = getNodeCoordinates(n, i, customers.length) })

  const getNodeColor = (node: NodeItem) => {
    if (node.id === disruptedNodeId) return '#ef4444' // Red: Disrupted
    if (!node.active) return '#64748b' // Grey: Inactive
    if (node.type === 'FACTORY' && disruptedNodeId) return '#f97316' // Orange: Degraded
    if (node.type === 'WAREHOUSE' && disruptedNodeId) return '#eab308' // Yellow: Stressed
    return '#10b981' // Green: Healthy
  }

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'PORT': return <Anchor className="w-3.5 h-3.5" />
      case 'FACTORY': return <Factory className="w-3.5 h-3.5" />
      case 'WAREHOUSE': return <Warehouse className="w-3.5 h-3.5" />
      case 'CUSTOMER': return <Users className="w-3.5 h-3.5" />
      default: return <Cpu className="w-3.5 h-3.5" />
    }
  }

  return (
    <div className="relative bg-slate-950/90 rounded-2xl border border-slate-800 p-4 overflow-hidden">
      {/* Header / Legend */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-3 border-b border-slate-800/80 pb-3">
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-ping" />
            MULTI-ECHELON TOPOLOGY INTERACTIVE MAP
          </h3>
          <p className="text-xs text-slate-400">
            29 Nodes & 34 Transit Links across India Electronics & Industrial Corridor
          </p>
        </div>

        {/* State Color Legend */}
        <div className="flex items-center space-x-3 text-xs">
          <span className="flex items-center gap-1 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Healthy
          </span>
          <span className="flex items-center gap-1 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> Stressed
          </span>
          <span className="flex items-center gap-1 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500" /> Degraded
          </span>
          <span className="flex items-center gap-1 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse" /> Disrupted
          </span>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="w-full overflow-x-auto">
        <svg viewBox="0 0 1000 520" className="w-full h-auto min-w-[750px]">
          {/* Echelon labels */}
          <text x="90" y="24" textAnchor="middle" fill="#94a3b8" fontSize="11" fontWeight="600">TIER-1 SUPPLIERS</text>
          <text x="270" y="24" textAnchor="middle" fill="#94a3b8" fontSize="11" fontWeight="600">CONTAINER PORTS</text>
          <text x="470" y="24" textAnchor="middle" fill="#94a3b8" fontSize="11" fontWeight="600">ASSEMBLY PLANTS</text>
          <text x="680" y="24" textAnchor="middle" fill="#94a3b8" fontSize="11" fontWeight="600">REGIONAL DCS</text>
          <text x="890" y="24" textAnchor="middle" fill="#94a3b8" fontSize="11" fontWeight="600">CUSTOMER HUBS</text>

          {/* Edges */}
          {edges.map((e) => {
            const p1 = nodePosMap[e.origin]
            const p2 = nodePosMap[e.destination]
            if (!p1 || !p2) return null

            const isDisruptedEdge = e.id === disruptedEdgeId || (disruptedNodeId && (e.origin === disruptedNodeId || e.destination === disruptedNodeId))
            const strokeColor = isDisruptedEdge ? '#ef4444' : '#334155'
            const strokeDash = isDisruptedEdge ? '5,5' : 'none'
            const strokeWidth = isDisruptedEdge ? 2.5 : 1.2

            return (
              <g key={e.id}>
                <line
                  x1={p1.x}
                  y1={p1.y}
                  x2={p2.x}
                  y2={p2.y}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={strokeDash}
                  opacity={isDisruptedEdge ? 0.9 : 0.45}
                />
              </g>
            )
          })}

          {/* Nodes */}
          {nodes.map((node) => {
            const pos = nodePosMap[node.id]
            if (!pos) return null

            const isDisruptedNode = node.id === disruptedNodeId
            const color = getNodeColor(node)
            const isSelected = selectedNode?.id === node.id

            return (
              <g
                key={node.id}
                className="cursor-pointer transition-transform hover:scale-110"
                onClick={() => setSelectedNode(node)}
              >
                {/* Glow ring for disrupted node */}
                {isDisruptedNode && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r="24"
                    fill="none"
                    stroke="#ef4444"
                    strokeWidth="2"
                    className="animate-ping opacity-75"
                  />
                )}

                {/* Outer halo */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={isSelected ? 18 : 14}
                  fill="#0f172a"
                  stroke={color}
                  strokeWidth={isSelected ? 3 : 2}
                />

                {/* Node center dot */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="7"
                  fill={color}
                />

                {/* Label */}
                <text
                  x={pos.x}
                  y={pos.y + 24}
                  textAnchor="middle"
                  fill={isDisruptedNode ? '#f87171' : '#cbd5e1'}
                  fontSize="9.5"
                  fontWeight={isDisruptedNode ? '700' : '500'}
                >
                  {node.city}
                </text>
              </g>
            )
          })}
        </svg>
      </div>

      {/* Selected Node Drawer */}
      {selectedNode && (
        <div className="mt-3 p-3 bg-slate-900/90 rounded-xl border border-slate-700 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center">
              {getNodeIcon(selectedNode.type)}
            </div>
            <div>
              <span className="font-bold text-white text-sm">{selectedNode.name}</span>
              <span className="ml-2 px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">
                {selectedNode.id}
              </span>
              <p className="text-slate-400 text-xs">
                {selectedNode.city}, {selectedNode.state} • Echelon: <span className="text-blue-300">{selectedNode.type}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div>
              <span className="text-slate-400 block text-[10px]">CRITICALITY</span>
              <span className="font-bold font-mono text-amber-400">
                {(selectedNode.criticality || 0.65).toFixed(2)}
              </span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">STATUS</span>
              <span className={`font-semibold ${selectedNode.id === disruptedNodeId ? 'text-rose-400' : 'text-emerald-400'}`}>
                {selectedNode.id === disruptedNodeId ? 'CHOKED / STRIKE' : 'OPERATIONAL'}
              </span>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
