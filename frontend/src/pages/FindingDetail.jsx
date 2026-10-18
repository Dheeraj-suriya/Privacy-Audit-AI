import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'
import { ArrowLeft, AlertTriangle, FileText, Shield, CheckCircle, XCircle, HelpCircle } from 'lucide-react'

export default function FindingDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [finding, setFinding] = useState(null)
  const [loading, setLoading] = useState(true)
  const [reviewComment, setReviewComment] = useState('')

  useEffect(() => {
    axios.get(`/api/findings/${id}`).then(res => {
      setFinding(res.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  const handleStatusChange = (status) => {
    axios.patch(`/api/findings/${id}`, { status, review_comment: reviewComment }).then(res => {
      setFinding(res.data)
    })
  }

  if (loading) return <div className="text-center py-20">Loading...</div>
  if (!finding) return <div className="text-center py-20 text-gray-500">Finding not found</div>

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/findings')} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Finding Details</h2>
            <span className={`badge-${finding.severity.toLowerCase()}`}>{finding.severity}</span>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">{finding.title}</h3>
        <p className="text-gray-600 dark:text-gray-300 leading-relaxed">{finding.description}</p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <div>
            <p className="text-sm text-gray-500">Category</p>
            <p className="font-medium text-gray-900 dark:text-white">{finding.category}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Risk Score</p>
            <p className="font-medium text-gray-900 dark:text-white">{finding.risk_score.toFixed(1)}/100</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Control</p>
            <p className="font-medium text-gray-900 dark:text-white">{finding.control_id || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Status</p>
            <p className="font-medium text-gray-900 dark:text-white">{finding.status}</p>
          </div>
        </div>
      </div>

      {finding.evidence && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Evidence</h3>
          </div>
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border-l-4 border-primary-500">
            <p className="text-sm text-gray-500 mb-1">From: {finding.evidence_document}</p>
            <p className="text-gray-700 dark:text-gray-300 text-sm italic">"{finding.evidence}"</p>
          </div>
        </div>
      )}

      {finding.recommendation && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <Shield className="w-5 h-5 text-accent-600" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recommendation</h3>
          </div>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{finding.recommendation}</p>
        </div>
      )}

      {/* Review Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Review Finding</h3>
        <textarea
          value={reviewComment}
          onChange={e => setReviewComment(e.target.value)}
          placeholder="Add review comment (optional)..."
          className="input-field mb-4 h-24 resize-none"
        />
        <div className="flex flex-wrap gap-3">
          <button onClick={() => handleStatusChange('ACCEPTED')} className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            <CheckCircle className="w-4 h-4" />
            Accept
          </button>
          <button onClick={() => handleStatusChange('REJECTED')} className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
            <XCircle className="w-4 h-4" />
            Reject
          </button>
          <button onClick={() => handleStatusChange('FALSE_POSITIVE')} className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
            <HelpCircle className="w-4 h-4" />
            False Positive
          </button>
          <button onClick={() => handleStatusChange('REVIEWED')} className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
            <AlertTriangle className="w-4 h-4" />
            Mark Reviewed
          </button>
        </div>
      </div>
    </div>
  )
}
