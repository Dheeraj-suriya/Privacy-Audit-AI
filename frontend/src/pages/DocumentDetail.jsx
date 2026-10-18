import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'
import { FileText, ArrowLeft, Hash, Calendar } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function DocumentDetail() {
  const { id } = useParams()
  const [doc, setDoc] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get(`/api/documents/${id}`).then(res => {
      setDoc(res.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  if (loading) return <div className="text-center py-20">Loading...</div>
  if (!doc) return <div className="text-center py-20 text-gray-500">Document not found</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/documents" className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Document Details</h2>
      </div>

      <div className="card">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
            <FileText className="w-7 h-7 text-primary-700" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{doc.original_filename}</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div>
                <p className="text-sm text-gray-500">File Type</p>
                <p className="font-medium text-gray-900 dark:text-white">{doc.file_type.toUpperCase()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Size</p>
                <p className="font-medium text-gray-900 dark:text-white">{(doc.file_size / 1024).toFixed(1)} KB</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <p className="font-medium text-gray-900 dark:text-white">{doc.status}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Extraction</p>
                <p className="font-medium text-gray-900 dark:text-white">{doc.extraction_method || 'Pending'}</p>
              </div>
            </div>
            <div className="flex items-center gap-6 mt-4 text-sm text-gray-500">
              <span className="flex items-center gap-1.5">
                <Hash className="w-4 h-4" />
                {doc.sha256.substring(0, 16)}...
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4" />
                {new Date(doc.created_at).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {doc.extracted_text && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Extracted Text</h3>
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto">
            <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono">
              {doc.extracted_text.substring(0, 5000)}
              {doc.extracted_text.length > 5000 && '...'}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
