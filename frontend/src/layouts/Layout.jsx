import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useState } from 'react'
import {
  Shield, LayoutDashboard, FileText, AlertTriangle, CheckSquare,
  MessageSquare, LogOut, Moon, Sun, Settings, Activity, GitBranch,
  ChevronLeft, ChevronRight
} from 'lucide-react'

export default function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [dark, setDark] = useState(false)
  const [collapsed, setCollapsed] = useState(false)

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/documents', icon: FileText, label: 'Documents' },
    { path: '/findings', icon: AlertTriangle, label: 'Findings' },
    { path: '/remediation', icon: CheckSquare, label: 'Remediation' },
    { path: '/processing-activities', icon: Activity, label: 'Processing' },
    { path: '/data-flows', icon: GitBranch, label: 'Data Flows' },
    { path: '/chat', icon: MessageSquare, label: 'AI Assistant' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ]

  const toggleDark = () => {
    setDark(!dark)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <div className={`min-h-screen ${dark ? 'dark' : ''}`}>
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        {/* Sidebar */}
        <aside className={`${collapsed ? 'w-20' : 'w-64'} bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-300`}>
          <div className="p-4 flex items-center gap-3 h-16 border-b border-gray-200 dark:border-gray-700">
            <Shield className="w-8 h-8 text-primary-700 flex-shrink-0" />
            {!collapsed && (
              <span className="text-lg font-bold text-primary-900 dark:text-white truncate">
                PrivacyAudit
              </span>
            )}
          </div>

          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navItems.map(item => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`sidebar-link ${isActive ? 'sidebar-link-active' : 'sidebar-link-inactive'}`}
                  title={collapsed ? item.label : ''}
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  {!collapsed && <span>{item.label}</span>}
                </Link>
              )
            })}
          </nav>

          <div className="p-3 border-t border-gray-200 dark:border-gray-700 space-y-1">
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="sidebar-link sidebar-link-inactive w-full justify-center"
            >
              {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
              {!collapsed && <span>Collapse</span>}
            </button>
            <button onClick={toggleDark} className="sidebar-link sidebar-link-inactive w-full">
              {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              {!collapsed && <span>{dark ? 'Light' : 'Dark'}</span>}
            </button>
            <button
              onClick={() => { logout(); navigate('/login') }}
              className="sidebar-link text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 w-full"
            >
              <LogOut className="w-5 h-5" />
              {!collapsed && <span>Logout</span>}
            </button>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3 flex justify-between items-center h-16">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              {navItems.find(n => n.path === location.pathname)?.label || 'PrivacyAudit AI'}
            </h1>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                <span className="text-sm font-semibold text-primary-700 dark:text-primary-300">
                  {user?.name?.[0]?.toUpperCase() || 'U'}
                </span>
              </div>
              <div className="text-sm">
                <p className="font-medium text-gray-900 dark:text-white">{user?.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{user?.role}</p>
              </div>
            </div>
          </header>
          <div className="flex-1 overflow-auto p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
