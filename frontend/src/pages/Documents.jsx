import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { useDropzone } from 'react-dropzone'
import { Link } from 'react-router-dom'
import {
  Upload, FileText, CheckCircle, AlertCircle, Loader,
  FileSpreadsheet, Image, FileCode, Trash2, Play
} from 'lucide-react'

const FILE_ICONS = {
  pdf: FileText,
  docx: FileText,
  xlsx: FileSpreadsheet,
  csv: FileSpreadsheet,
  txt: FileCode,
  image: Image,
}

const STATUS_STYLES = {
  UPLOADED: 'text-gray-500',
  PROCESSING: 'text-blue-500',
  EXTRACTED: 'text-green-500',
  ANALYZING: 'text-purple-500',
  COMPLETED: 'text-green-600',
  FAILED: 'text-red-500',
}

export default function Documents() {
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  useEffect(() => { fetchDocuments() }, [])

  const fetchDocuments = () => {
  axios.get('/api/documents/documents')
    .then(res => setDocuments(res.data.items))
    .catch(err => {
      console.error('Failed to fetch documents:', err)
    })
}

  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles.length === 0) return
    setUploading(true)
    setUploadProgress(0)
    const formData = new FormData()
    formData.append('file', acceptedFiles[0])

    axios.post('/api/documents/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        setUploadProgress(percent)
      }
    }).then(() => {
      fetchDocuments()
      setUploading(false)
      setUploadProgress(0)
    }).catch(() => {
      setUploading(false)
      setUploadProgress(0)
    })
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv'],
      'text/plain': ['.txt'],
      'image/*': ['.png', '.jpg', '.jpeg'],
    },
    maxSize: 25 * 1024 * 1024,
  })

  const handleAnalyze = (docId) => {
  axios.post(`/api/analysis/analysis/${docId}/start`)
    .then((res) => {
      console.log('ANALYSIS START RESPONSE:', res.data)

      const analysisId =
        res.data?.id ??
        res.data?.analysis_id ??
        res.data?.analysis?.id

      if (!analysisId) {
        console.error(
          '❌ Analysis started but backend did not return an Analysis ID:',
          res.data
        )
        return
      }

      // Store latest analysis ID
      localStorage.setItem(
        'privacyAuditAnalysisId',
        String(analysisId)
      )

      console.log('✅ NEW ANALYSIS ID:', analysisId)
      console.log(
        '✅ STORED ID:',
        localStorage.getItem('privacyAuditAnalysisId')
      )

      // Tell other pages/components that a new analysis exists
      window.dispatchEvent(
        new Event('privacyAuditAnalysisChanged')
      )

      setTimeout(() => {
        fetchDocuments()
      }, 1000)
    })
    .catch((err) => {
      console.error(
        '❌ Analysis failed:',
        err.response?.data || err.message
      )
    })
}

  const handleDelete = (docId) => {
    if (!confirm('Delete this document?')) return
    axios.delete(`/api/documents/documents/${docId}`).then(() => fetchDocuments())
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Documents</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">{documents.length} documents</p>
      </div>

      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragActive ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-10 h-10 mx-auto text-gray-400 mb-3" />
        {uploading ? (
          <div className="space-y-2">
            <p className="text-primary-600 font-medium">Uploading... {uploadProgress}%</p>
            <div className="w-48 h-2 bg-gray-200 rounded-full mx-auto overflow-hidden">
              <div className="h-full bg-primary-600 rounded-full transition-all" style={{ width: `${uploadProgress}%` }}></div>
            </div>
          </div>
        ) : isDragActive ? (
          <p className="text-primary-600 font-medium">Drop the file here</p>
        ) : (
          <div>
            <p className="text-gray-600 dark:text-gray-300 font-medium">Drag & drop files here, or click to select</p>
            <p className="text-sm text-gray-400 mt-1">PDF, DOCX, XLSX, CSV, TXT, PNG, JPG (max 25MB)</p>
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Uploaded Documents</h3>
        <div className="space-y-3">
          {documents.length > 0 ? documents.map(doc => {
            const Icon = FILE_ICONS[doc.file_type] || FileText
            return (
              <div key={doc.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg group">
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="w-10 h-10 bg-white dark:bg-gray-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-gray-500" />
                  </div>
                  <div className="min-w-0">
                    <Link to={`/documents/${doc.id}`} className="font-medium text-gray-900 dark:text-white hover:text-primary-600 truncate block">
                      {doc.original_filename}
                    </Link>
                    <p className="text-sm text-gray-500">
                      {(doc.file_size / 1024).toFixed(1)} KB • {doc.file_type.toUpperCase()} •
                      <span className={`ml-1 font-medium ${STATUS_STYLES[doc.status] || 'text-gray-500'}`}>{doc.status}</span>
                      {doc.extraction_method && ` • ${doc.extraction_method}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {doc.status === 'EXTRACTED' && (
                    <button
                      onClick={() => handleAnalyze(doc.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-700 text-white text-sm rounded-lg hover:bg-primary-800 transition-colors"
                    >
                      <Play className="w-3.5 h-3.5" />
                      Analyze
                    </button>
                  )}
                  {doc.status === 'COMPLETED' && (
                    <span className="flex items-center gap-1 text-green-600 text-sm">
                      <CheckCircle className="w-4 h-4" />
                      Done
                    </span>
                  )}
                  {doc.status === 'FAILED' && (
                    <span className="flex items-center gap-1 text-red-500 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      Failed
                    </span>
                  )}
                  {doc.status === 'PROCESSING' && (
                    <Loader className="w-4 h-4 text-blue-500 animate-spin" />
                  )}
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-1.5 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )
          }) : (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 dark:text-gray-400">No documents uploaded yet</p>
              <p className="text-sm text-gray-400 mt-1">Upload a privacy policy or data inventory to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
