import React from 'react'
import { NodeItem, EdgeItem } from '../types'
import { NetworkMap } from '../components/NetworkMap'
import { Cpu, Layers, Box, CheckCircle2 } from 'lucide-react'

interface NetworkViewProps {
  nodes: NodeItem[]
  edges: EdgeItem[]
}

export const NetworkView: React.FC<NetworkViewProps> = ({ nodes, edges }) => {
  const products = [
    { id: 'FG_SMART_IOT', name: 'Industrial IoT Gateway', price: '₹7,500', penalty: '₹5,000', bom: '1x RM_CHIP + 1x RM_CHASSIS + 1x RM_POLYMER' },
    { id: 'FG_TELECOM_NODE', name: 'Secure 5G Edge Node', price: '₹12,000', penalty: '₹9,000', bom: '2x RM_CHIP + 1x RM_CHASSIS + 2x RM_POLYMER' },
    { id: 'FG_CONTROLLER', name: 'Smart Power Controller', price: '₹9,000', penalty: '₹6,500', bom: '1x RM_CHIP + 2x RM_CHASSIS + 1x RM_POLYMER' },
    { id: 'RM_CHIP', name: 'Microcontroller & SoC', price: '₹1,200', penalty: '₹3,000', bom: 'Tier-1 Raw Material (Taiwan / Seoul / Bengaluru)' },
    { id: 'RM_CHASSIS', name: 'Aluminum Enclosure', price: '₹800', penalty: '₹1,500', bom: 'Tier-1 Raw Material (Bhilai / Jamshedpur / Chennai)' },
    { id: 'RM_POLYMER', name: 'Thermal Polymer Resin', price: '₹400', penalty: '₹800', bom: 'Tier-1 Raw Material (Gujarat / Thane)' },
  ]

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            <span>FULL SUPPLY-CHAIN TOPOLOGY & BILL OF MATERIALS (BOM)</span>
          </h2>
          <p className="text-xs text-slate-400">
            Digital twin multi-echelon network: 8 Suppliers, 2 Ports, 3 Factories, 4 Warehouses, 12 Customer Cities.
          </p>
        </div>
      </div>

      <NetworkMap nodes={nodes} edges={edges} />

      {/* Bill of Materials & Product Portfolio */}
      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Box className="w-4 h-4 text-blue-400" />
            <span>PRODUCT PORTFOLIO & INPUT BILL OF MATERIALS (BOM)</span>
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
              <tr>
                <th className="px-4 py-3">PRODUCT ID</th>
                <th className="px-4 py-3">PRODUCT NAME</th>
                <th className="px-4 py-3">SELLING PRICE</th>
                <th className="px-4 py-3">STOCKOUT PENALTY</th>
                <th className="px-4 py-3">BOM INPUT SPECIFICATION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {products.map((p) => (
                <tr key={p.id} className="hover:bg-slate-800/40">
                  <td className="px-4 py-3 text-blue-400 font-bold">{p.id}</td>
                  <td className="px-4 py-3 text-white font-sans font-medium">{p.name}</td>
                  <td className="px-4 py-3 text-emerald-400">{p.price}</td>
                  <td className="px-4 py-3 text-rose-400">{p.penalty}</td>
                  <td className="px-4 py-3 text-slate-300 font-sans">{p.bom}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
