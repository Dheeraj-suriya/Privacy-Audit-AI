import { Link } from 'react-router-dom'
import { Shield, Upload, Search, BarChart3, MessageSquare, CheckCircle, Lock, FileCheck } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700">
      {/* Hero */}
      <nav className="px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Shield className="w-8 h-8 text-white" />
          <span className="text-xl font-bold text-white">PrivacyAudit AI</span>
        </div>
        <div className="flex gap-4">
          <Link to="/login" className="px-4 py-2 text-white hover:text-primary-200 transition-colors">Sign In</Link>
          <Link to="/register" className="px-5 py-2 bg-white text-primary-900 rounded-lg font-medium hover:bg-primary-50 transition-colors">Get Started</Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
          AI-Powered Privacy<br />Impact Assessment
        </h1>
        <p className="text-xl text-primary-200 mb-10 max-w-2xl mx-auto">
          Discover personal-data risks, assess privacy controls, and track remediation from one intelligent dashboard.
        </p>
        <div className="flex gap-4 justify-center">
          <Link to="/register" className="px-8 py-4 bg-white text-primary-900 rounded-xl font-semibold text-lg hover:bg-primary-50 transition-colors shadow-lg">
            Start Privacy Audit
          </Link>
          <Link to="/login" className="px-8 py-4 border-2 border-white text-white rounded-xl font-semibold text-lg hover:bg-white/10 transition-colors">
            View Demo
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="bg-white dark:bg-gray-900 py-20">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Upload, title: 'Upload Documents', desc: 'Drag and drop privacy policies, data inventories, and vendor agreements.' },
              { icon: Search, title: 'AI Analysis', desc: 'Automatic PII detection, compliance scoring, and risk assessment.' },
              { icon: BarChart3, title: 'Track Remediation', desc: 'Kanban-style task board with assignments and progress tracking.' },
            ].map((f, i) => (
              <div key={i} className="card text-center">
                <div className="w-14 h-14 mx-auto mb-4 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center">
                  <f.icon className="w-7 h-7 text-primary-700" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{f.title}</h3>
                <p className="text-gray-600 dark:text-gray-400">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="bg-gray-50 dark:bg-gray-800 py-20">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">Key Features</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: FileCheck, title: 'DPDP Compliance', desc: '12 configurable controls aligned with privacy regulations.' },
              { icon: Lock, title: 'PII Detection', desc: 'Multi-layer detection with regex, NER, and contextual analysis.' },
              { icon: MessageSquare, title: 'AI Assistant', desc: 'RAG-based chat that answers questions from your documents.' },
              { icon: CheckCircle, title: 'Remediation', desc: 'Create, assign, and track privacy remediation tasks.' },
            ].map((f, i) => (
              <div key={i} className="card">
                <f.icon className="w-6 h-6 text-accent-600 mb-3" />
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{f.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-primary-900 py-8 text-center">
        <p className="text-primary-300 text-sm">
          PrivacyAudit AI — AI-assisted assessment tool. Not legal advice.
        </p>
      </footer>
    </div>
  )
}
