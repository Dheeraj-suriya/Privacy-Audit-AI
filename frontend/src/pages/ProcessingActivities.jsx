import { useState, useEffect } from 'react'
import axios from 'axios'
import { Activity, Plus, Globe, Database, Users } from 'lucide-react'

export default function ProcessingActivities() {
  const [activities, setActivities] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [newActivity, setNewActivity] = useState({
    name: '', purpose: '', data_subjects: '', data_categories: '',
    storage_location: '', retention_period: '', risk_level: 'LOW'
  })

  useEffect(() => {
    axios.get('/api/data-inventory/processing-activities').then(res => setActivities(res.data))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    axios.post('/api/data-inventory/processing-activities', newActivity).then(() => {
      setShowForm(false)
      setNewActivity({ name: '', purpose: '', data_subjects: '', data_categories: '', storage_location: '', retention_period: '', risk_level: 'LOW' })
      axios.get('/api/data-inventory/processing-activities').then(res => setActivities(res.data))
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Processing Activities</h2>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Activity
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">New Processing Activity</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input className="input-field" placeholder="Activity Name" value={newActivity.name} onChange={e => setNewActivity({...newActivity, name: e.target.value})} required />
            <input className="input-field" placeholder="Purpose" value={newActivity.purpose} onChange={e => setNewActivity({...newActivity, purpose: e.target.value})} />
            <input className="input-field" placeholder="Data Subjects (e.g., Customers, Employees)" value={newActivity.data_subjects} onChange={e => setNewActivity({...newActivity, data_subjects: e.target.value})} />
            <input className="input-field" placeholder="Data Categories (e.g., Contact, Financial)" value={newActivity.data_categories} onChange={e => setNewActivity({...newActivity, data_categories: e.target.value})} />
            <input className="input-field" placeholder="Storage Location" value={newActivity.storage_location} onChange={e => setNewActivity({...newActivity, storage_location: e.target.value})} />
            <input className="input-field" placeholder="Retention Period" value={newActivity.retention_period} onChange={e => setNewActivity({...newActivity, retention_period: e.target.value})} />
            <select className="input-field" value={newActivity.risk_level} onChange={e => setNewActivity({...newActivity, risk_level: e.target.value})}>
              <option value="LOW">Low Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="HIGH">High Risk</option>
              <option value="CRITICAL">Critical Risk</option>
            </select>
            <div className="flex gap-3 md:col-span-2">
              <button type="submit" className="btn-primary">Save Activity</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {activities.length > 0 ? activities.map(act => (
          <div key={act.id} className="card">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                  <Activity className="w-5 h-5 text-primary-700" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">{act.name}</h3>
                  <p className="text-sm text-gray-500">{act.purpose}</p>
                </div>
              </div>
              <span className={`badge-${act.risk_level.toLowerCase()}`}>{act.risk_level}</span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Users className="w-4 h-4" />
                {act.data_subjects || 'Not specified'}
              </div>
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Database className="w-4 h-4" />
                {act.storage_location || 'Not specified'}
              </div>
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Globe className="w-4 h-4" />
                {act.cross_border_transfer ? 'Cross-border' : 'Local'}
              </div>
              <div className="text-gray-600 dark:text-gray-400">
                Retention: {act.retention_period || 'Not specified'}
              </div>
            </div>
          </div>
        )) : (
          <div className="card md:col-span-2 text-center py-12">
            <Activity className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No processing activities yet. Upload documents or add manually.</p>
          </div>
        )}
      </div>
    </div>
  )
}
