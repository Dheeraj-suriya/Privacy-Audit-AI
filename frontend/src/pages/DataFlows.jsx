import { useState, useEffect } from 'react'
import axios from 'axios'
import { GitBranch, ArrowRight, Plus, Database, Server } from 'lucide-react'

export default function DataFlows() {
  const [flows, setFlows] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [newFlow, setNewFlow] = useState({ source: '', destination: '', data_categories: '', purpose: '', risk_level: 'LOW' })

  useEffect(() => {
    axios.get('/api/data-inventory/data-flows').then(res => setFlows(res.data))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    axios.post('/api/data-inventory/data-flows', newFlow).then(() => {
      setShowForm(false)
      setNewFlow({ source: '', destination: '', data_categories: '', purpose: '', risk_level: 'LOW' })
      axios.get('/api/data-inventory/data-flows').then(res => setFlows(res.data))
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Data Flows</h2>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Flow
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">New Data Flow</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input className="input-field" placeholder="Source (e.g., Website)" value={newFlow.source} onChange={e => setNewFlow({...newFlow, source: e.target.value})} required />
            <input className="input-field" placeholder="Destination (e.g., Database)" value={newFlow.destination} onChange={e => setNewFlow({...newFlow, destination: e.target.value})} required />
            <input className="input-field" placeholder="Data Categories" value={newFlow.data_categories} onChange={e => setNewFlow({...newFlow, data_categories: e.target.value})} />
            <input className="input-field md:col-span-2" placeholder="Purpose" value={newFlow.purpose} onChange={e => setNewFlow({...newFlow, purpose: e.target.value})} />
            <select className="input-field" value={newFlow.risk_level} onChange={e => setNewFlow({...newFlow, risk_level: e.target.value})}>
              <option value="LOW">Low Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="HIGH">High Risk</option>
              <option value="CRITICAL">Critical Risk</option>
            </select>
            <div className="flex gap-3 md:col-span-3">
              <button type="submit" className="btn-primary">Save Flow</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-4">
        {flows.length > 0 ? flows.map(flow => (
          <div key={flow.id} className="card">
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                    <Server className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">{flow.source}</p>
                    <p className="text-xs text-gray-500">Source</p>
                  </div>
                </div>
              </div>
              <div className="flex flex-col items-center px-4">
                <ArrowRight className="w-6 h-6 text-gray-400" />
                <span className="text-xs text-gray-500 mt-1">{flow.data_categories || 'Data'}</span>
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                    <Database className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">{flow.destination}</p>
                    <p className="text-xs text-gray-500">Destination</p>
                  </div>
                </div>
              </div>
              <span className={`badge-${flow.risk_level.toLowerCase()}`}>{flow.risk_level}</span>
            </div>
            {flow.purpose && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 pl-14">Purpose: {flow.purpose}</p>
            )}
          </div>
        )) : (
          <div className="card text-center py-12">
            <GitBranch className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No data flows detected yet. Upload documents or add manually.</p>
          </div>
        )}
      </div>
    </div>
  )
}
