import { useEffect, useState } from 'react'
import axios from 'axios'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, LineChart, Line
} from 'recharts'
import {
  AlertTriangle, FileText, CheckCircle, Clock, Shield,
  TrendingUp, Users, Activity
} from 'lucide-react'

const RISK_COLORS = {
  CRITICAL: '#dc2626',
  HIGH: '#ea580c',
  MEDIUM: '#ca8a04',
  LOW: '#16a34a',
}

const POSTURE_STYLES = {
  'Good': 'text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-300',
  'Needs Attention': 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30 dark:text-yellow-300',
  'High Risk': 'text-orange-600 bg-orange-100 dark:bg-orange-900/30 dark:text-orange-300',
  'Critical': 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-300',
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get('/api/dashboard/dashboard')
      .then(res => { setData(res.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700"></div>
    </div>
  )
  if (!data) return <div className="text-center py-20 text-gray-500">Failed to load dashboard</div>

  const { summary, risk_distribution, compliance_by_category, remediation_progress, recent_findings, personal_data_categories } = data

  const riskData = [
    { name: 'Critical', value: risk_distribution.critical, color: RISK_COLORS.CRITICAL },
    { name: 'High', value: risk_distribution.high, color: RISK_COLORS.HIGH },
    { name: 'Medium', value: risk_distribution.medium, color: RISK_COLORS.MEDIUM },
    { name: 'Low', value: risk_distribution.low, color: RISK_COLORS.LOW },
  ].filter(d => d.value > 0)

  const piiData = Object.entries(personal_data_categories).map(([name, value]) => ({ name, value }))

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-primary-700" />
            </div>
            <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${POSTURE_STYLES[summary.posture] || POSTURE_STYLES['Needs Attention']}`}>
              {summary.posture}
            </span>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Privacy Score</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{summary.privacy_score}<span className="text-lg text-gray-400">/100</span></p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            {summary.critical_risks > 0 && (
              <span className="badge-critical">{summary.critical_risks} Critical</span>
            )}
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Risk Level</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{summary.critical_risks > 0 ? 'Critical' : summary.high_risks > 0 ? 'High' : 'Medium'}</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Documents</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{summary.documents_analyzed}</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-orange-600" />
            </div>
            {summary.overdue_tasks > 0 && (
              <span className="badge-high">{summary.overdue_tasks} Overdue</span>
            )}
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Open Tasks</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{summary.open_remediation_tasks}</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={riskData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" paddingAngle={4}>
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-2">
            {riskData.map(d => (
              <div key={d.name} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }}></div>
                <span className="text-xs text-gray-600 dark:text-gray-400">{d.name}: {d.value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compliance by Category</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={compliance_by_category} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} />
              <YAxis dataKey="category" type="category" width={100} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value) => [`${value}%`, 'Score']} />
              <Bar dataKey="score" fill="#334e68" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Personal Data Categories</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={piiData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-20} textAnchor="end" height={60} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#7c3aed" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Remediation Progress */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Remediation Progress</h3>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-green-600">{remediation_progress.resolution_percentage}% resolved</span>
          </div>
        </div>
        <div className="grid grid-cols-5 gap-4">
          {[
            { label: 'Open', count: remediation_progress.open, color: 'bg-gray-200 dark:bg-gray-700' },
            { label: 'In Progress', count: remediation_progress.in_progress, color: 'bg-blue-200 dark:bg-blue-900/30' },
            { label: 'Blocked', count: remediation_progress.blocked, color: 'bg-red-200 dark:bg-red-900/30' },
            { label: 'Resolved', count: remediation_progress.resolved, color: 'bg-green-200 dark:bg-green-900/30' },
            { label: 'Closed', count: remediation_progress.closed, color: 'bg-primary-200 dark:bg-primary-900/30' },
          ].map(item => (
            <div key={item.label} className="text-center">
              <div className={`${item.color} rounded-lg p-4 mb-2`}>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{item.count}</p>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">{item.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Findings */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Findings</h3>
        <div className="space-y-3">
          {recent_findings.length > 0 ? recent_findings.slice(0, 5).map(finding => (
            <div key={finding.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 dark:text-white truncate">{finding.title}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{finding.category} • {finding.status}</p>
              </div>
              <span className={`badge-${finding.severity.toLowerCase()} ml-4 flex-shrink-0`}>{finding.severity}</span>
            </div>
          )) : (
            <p className="text-center text-gray-500 py-8">No findings yet. Upload and analyze documents to get started.</p>
          )}
        </div>
      </div>
    </div>
  )
}
