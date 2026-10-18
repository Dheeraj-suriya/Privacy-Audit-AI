import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  CheckSquare, Plus, Clock, AlertTriangle, CheckCircle,
  XCircle, User, Calendar, MessageSquare
} from 'lucide-react'

const COLUMNS = [
  { id: 'OPEN', label: 'Open', color: 'bg-gray-100 dark:bg-gray-700/50' },
  { id: 'IN_PROGRESS', label: 'In Progress', color: 'bg-blue-50 dark:bg-blue-900/20' },
  { id: 'BLOCKED', label: 'Blocked', color: 'bg-red-50 dark:bg-red-900/20' },
  { id: 'RESOLVED', label: 'Resolved', color: 'bg-green-50 dark:bg-green-900/20' },
]

const PRIORITY_COLORS = {
  CRITICAL: 'text-red-600 bg-red-100 dark:bg-red-900/30',
  HIGH: 'text-orange-600 bg-orange-100 dark:bg-orange-900/30',
  MEDIUM: 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30',
  LOW: 'text-green-600 bg-green-100 dark:bg-green-900/30',
}

export default function Remediation() {
  const [tasks, setTasks] = useState([])
  const [findings, setFindings] = useState([])
  const [progress, setProgress] = useState(null)
  const [showForm, setShowForm] = useState(false)

  const [newTask, setNewTask] = useState({
    finding_id: '',
    title: '',
    description: '',
    priority: 'MEDIUM',
    due_date: ''
})

const [loading, setLoading] = useState(true)

  useEffect(() => { fetchData() }, [])

  const fetchData = () => {
    axios.get('/api/remediation/remediation').then(res => {
      setTasks(res.data)
      setLoading(false)
    })

    axios.get('/api/remediation/remediation/progress')
    .then(res => setProgress(res.data))

    axios.get('/api/findings/')
    .then(res => setFindings(res.data))
    .catch(err => {
      console.error('Failed to load findings:', err.response?.data || err)
    })
  }

  const handleCreate = (e) => {
    e.preventDefault()
    const payload = {
      finding_id: Number(newTask.finding_id),
      title: newTask.title,
      description: newTask.description,
      priority: newTask.priority,
      due_date: newTask.due_date
      ? `${newTask.due_date}T00:00:00`
      : null,
    }

  console.log('Creating remediation task:', payload)

  axios.post('/api/remediation/remediation', payload)
    .then(() => {
      setShowForm(false)

      setNewTask({
        finding_id: '',
        title: '',
        description: '',
        priority: 'MEDIUM',
        due_date: ''
      })

      fetchData()
    })
    .catch(err => {
      console.error(
        'Failed to create remediation task:',
        err.response?.data || err
      )
    })
  }

  const handleMove = (taskId, newStatus) => {
    axios.patch(`/api/remediation/remediation/${taskId}`, { status: newStatus }).then(() => fetchData())
    .catch(err => {
      console.error('Failed to update remediation task:', err)
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Remediation Board</h2>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          New Task
        </button>
      </div>

      {/* Progress */}
      {progress && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900 dark:text-white">Progress Overview</h3>
            <span className="text-sm font-medium text-green-600">{progress.resolution_percentage}% Resolved</span>
          </div>
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div className="h-full bg-green-500 rounded-full transition-all" style={{ width: `${progress.resolution_percentage}%` }}></div>
          </div>
          <div className="grid grid-cols-5 gap-4 mt-4 text-center">
            {[
              { label: 'Total', value: progress.total },
              { label: 'Open', value: progress.open },
              { label: 'In Progress', value: progress.in_progress },
              { label: 'Blocked', value: progress.blocked },
              { label: 'Overdue', value: progress.overdue, highlight: true },
            ].map(item => (
              <div key={item.label}>
                <p className={`text-2xl font-bold ${item.highlight ? 'text-red-600' : 'text-gray-900 dark:text-white'}`}>{item.value}</p>
                <p className="text-xs text-gray-500">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* New Task Form */}
      {showForm && (
        <div className="card border-2 border-primary-200 dark:border-primary-800">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Create Remediation Task</h3>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
             <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Finding
              </label>
              <select
              value={newTask.finding_id}
              onChange={e =>
                setNewTask({
                  ...newTask,
                  finding_id: e.target.value
                })
              }
              className="input-field"
              required
              >
                <option value="">Select a finding</option>
                
                {findings.map(finding => (
                  <option key={finding.id} value={finding.id}>
                    {finding.title}
                  </option>
                ))}
                </select>
              </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Title
              </label>
              
              <input
               value={newTask.title}
               onChange={e =>
                setNewTask({
                  ...newTask,
                  title: e.target.value
                })
              }
              className="input-field"
              placeholder="e.g., Update Privacy Notice"
              required
             />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
              <textarea
                value={newTask.description}
                onChange={e => setNewTask({ ...newTask, description: e.target.value })}
                className="input-field h-20 resize-none"
                placeholder="Describe the remediation action..."
              />
            </div>
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Priority</label>
                <select
                  value={newTask.priority}
                  onChange={e => setNewTask({ ...newTask, priority: e.target.value })}
                  className="input-field"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Due Date</label>
                <input
                  type="date"
                  value={newTask.due_date}
                  onChange={e => setNewTask({ ...newTask, due_date: e.target.value })}
                  className="input-field"
                />
              </div>
            </div>
            <div className="flex gap-3">
              <button type="submit" className="btn-primary">Create Task</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {COLUMNS.map(col => (
          <div key={col.id} className="flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm">{col.label}</h3>
              <span className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                {tasks.filter(t => t.status === col.id).length}
              </span>
            </div>
            <div className={`${col.color} rounded-xl p-3 space-y-3 min-h-[200px]`}>
              {tasks.filter(t => t.status === col.id).map(task => (
                <div key={task.id} className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-white text-sm">{task.title}</h4>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${PRIORITY_COLORS[task.priority]}`}>
                      {task.priority}
                    </span>
                  </div>
                  {task.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">{task.description}</p>
                  )}
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}
                    </div>
                    {task.assigned_to && (
                      <div className="flex items-center gap-1">
                        <User className="w-3 h-3" />
                        {task.assignee_name}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-1 mt-3">
                    {col.id !== 'OPEN' && (
                      <button onClick={() => handleMove(task.id, 'OPEN')} className="text-xs px-2 py-1 bg-gray-100 rounded hover:bg-gray-200">← Open</button>
                    )}
                    {col.id !== 'IN_PROGRESS' && col.id !== 'RESOLVED' && (
                      <button onClick={() => handleMove(task.id, 'IN_PROGRESS')} className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200">Start →</button>
                    )}
                    {col.id !== 'BLOCKED' && col.id !== 'RESOLVED' && (
                      <button onClick={() => handleMove(task.id, 'BLOCKED')} className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200">Block</button>
                    )}
                    {col.id !== 'RESOLVED' && (
                      <button onClick={() => handleMove(task.id, 'RESOLVED')} className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200">Resolve ✓</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
