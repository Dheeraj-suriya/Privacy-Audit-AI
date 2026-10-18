import { useState, useEffect } from 'react'
import axios from 'axios'
import { Link } from 'react-router-dom'
import { AlertTriangle, Search, ChevronRight } from 'lucide-react'

export default function Findings() {
  const [findings, setFindings] = useState([])
  const [filters, setFilters] = useState({
    severity: '',
    status: '',
    category: ''
  })
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  // Fetch findings when page loads
  useEffect(() => {
  fetchFindings()

  const handleAnalysisChanged = () => {
    console.log('🔄 Analysis ID changed, refreshing findings...')
    fetchFindings()
  }

  window.addEventListener(
    'privacyAuditAnalysisChanged',
    handleAnalysisChanged
  )

  return () => {
    window.removeEventListener(
      'privacyAuditAnalysisChanged',
      handleAnalysisChanged
    )
  }
}, [])

  const fetchFindings = () => {
  setLoading(true)

  const analysisId = localStorage.getItem(
    'privacyAuditAnalysisId'
  )

  console.log(
    '🔍 CURRENT ANALYSIS ID:',
    analysisId
  )

  if (!analysisId) {
    console.error('❌ No Analysis ID found')
    setFindings([])
    setLoading(false)
    return
  }

  axios
    .get(`/api/analysis/analysis/${analysisId}/findings`)
    .then((res) => {
      console.log(
        `✅ FINDINGS FOR ANALYSIS ${analysisId}:`,
        res.data
      )

      const data = Array.isArray(res.data)
        ? res.data
        : res.data?.findings ||
          res.data?.items ||
          []

      setFindings(data)
      setLoading(false)
    })
    .catch((err) => {
      console.error(
        '❌ Failed to load findings:',
        err.response?.data || err.message
      )

      setFindings([])
      setLoading(false)
    })
}

  // Apply filters on the frontend
  const filtered = findings.filter((f) => {
    const title = f.title || ''
    const description = f.description || ''
    const severity = f.severity || ''
    const status = f.status || ''
    const category = f.category || ''

    const matchesSearch =
      title.toLowerCase().includes(search.toLowerCase()) ||
      description.toLowerCase().includes(search.toLowerCase())

    const matchesSeverity =
      !filters.severity || severity === filters.severity

    const matchesStatus =
      !filters.status || status === filters.status

    const matchesCategory =
      !filters.category || category === filters.category

    return (
      matchesSearch &&
      matchesSeverity &&
      matchesStatus &&
      matchesCategory
    )
  })

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Findings
        </h2>

        <span className="text-sm text-gray-500">
          {filtered.length} findings
        </span>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4">

          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />

            <input
              type="text"
              placeholder="Search findings..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-field pl-9"
            />
          </div>

          {/* Severity */}
          <select
            value={filters.severity}
            onChange={(e) =>
              setFilters({
                ...filters,
                severity: e.target.value
              })
            }
            className="input-field w-40"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          {/* Status */}
          <select
            value={filters.status}
            onChange={(e) =>
              setFilters({
                ...filters,
                status: e.target.value
              })
            }
            className="input-field w-40"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="REVIEWED">Reviewed</option>
            <option value="ACCEPTED">Accepted</option>
            <option value="REJECTED">Rejected</option>
            <option value="FALSE_POSITIVE">False Positive</option>
          </select>

        </div>
      </div>

      {/* Findings Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">

          <table className="w-full">

            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">

                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400">
                  Finding
                </th>

                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400">
                  Category
                </th>

                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400">
                  Severity
                </th>

                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400">
                  Score
                </th>

                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400">
                  Status
                </th>

                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400">
                  Date
                </th>

                <th></th>

              </tr>
            </thead>

            <tbody>

              {loading ? (

                <tr>
                  <td
                    colSpan="7"
                    className="text-center py-12"
                  >
                    Loading...
                  </td>
                </tr>

              ) : filtered.length > 0 ? (

                filtered.map((f) => (

                  <tr
                    key={f.id}
                    className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
                  >

                    {/* Finding */}
                    <td className="py-3 px-4">

                      <p className="font-medium text-gray-900 dark:text-white">
                        {f.title || 'Untitled Finding'}
                      </p>

                      <p className="text-sm text-gray-500 truncate max-w-xs">
                        {f.description || 'No description available'}
                      </p>

                    </td>

                    {/* Category */}
                    <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                      {f.category || '-'}
                    </td>

                    {/* Severity */}
                    <td className="py-3 px-4">

                      <span
                        className={`badge-${(f.severity || 'LOW').toLowerCase()}`}
                      >
                        {f.severity || 'LOW'}
                      </span>

                    </td>

                    {/* Risk Score */}
                    <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">
                      {typeof f.risk_score === 'number'
                        ? f.risk_score.toFixed(1)
                        : '-'}
                    </td>

                    {/* Status */}
                    <td className="py-3 px-4">

                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {f.status || '-'}
                      </span>

                    </td>

                    {/* Date */}
                    <td className="py-3 px-4 text-sm text-gray-500">

                      {f.created_at
                        ? new Date(f.created_at).toLocaleDateString()
                        : '-'}

                    </td>

                    {/* Details */}
                    <td className="py-3 px-4">

                      <Link
                        to={`/findings/${f.id}`}
                        className="text-primary-600 hover:text-primary-800"
                      >
                        <ChevronRight className="w-5 h-5" />
                      </Link>

                    </td>

                  </tr>

                ))

              ) : (

                <tr>

                  <td
                    colSpan="7"
                    className="text-center py-12 text-gray-500"
                  >

                    <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-gray-300" />

                    No findings match your filters

                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>
      </div>

    </div>
  )
}