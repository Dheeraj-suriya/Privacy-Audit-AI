import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Shield, User, Bell, Lock, HelpCircle } from 'lucide-react'

export default function Settings() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('profile')

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'help', label: 'Help', icon: HelpCircle },
  ]

  return (
    <div className="space-y-6 max-w-3xl">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h2>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-48 space-y-1">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300'
                  : 'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700/50'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 card">
          {activeTab === 'profile' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Profile Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
                  <input className="input-field" value={user?.name || ''} readOnly />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
                  <input className="input-field" value={user?.email || ''} readOnly />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Role</label>
                  <input className="input-field" value={user?.role || ''} readOnly />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Organization ID</label>
                  <input className="input-field" value={user?.organization_id || ''} readOnly />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Security Settings</h3>
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="w-5 h-5 text-yellow-600" />
                  <p className="font-medium text-yellow-800 dark:text-yellow-300">Password Management</p>
                </div>
                <p className="text-sm text-yellow-700 dark:text-yellow-400">Password changes are managed through your administrator.</p>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Notification Preferences</h3>
              <div className="space-y-3">
                {['New findings detected', 'Remediation task assigned', 'Analysis completed', 'Risk score changes'].map((label, i) => (
                  <label key={i} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg cursor-pointer">
                    <input type="checkbox" defaultChecked className="w-4 h-4 text-primary-600 rounded" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'help' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">About PrivacyAudit AI</h3>
              <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
                <p>PrivacyAudit AI is an AI-assisted privacy impact assessment tool designed to help organizations understand their privacy posture.</p>
                <p><strong>Important:</strong> This tool does not constitute legal advice. All assessments should be reviewed by qualified privacy professionals.</p>
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>Features:</strong> Document analysis, PII detection, compliance scoring, risk assessment, remediation tracking, and AI-powered Q&A.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
