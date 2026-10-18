import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './layouts/Layout'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import DocumentDetail from './pages/DocumentDetail'
import Findings from './pages/Findings'
import FindingDetail from './pages/FindingDetail'
import Remediation from './pages/Remediation'
import ProcessingActivities from './pages/ProcessingActivities'
import DataFlows from './pages/DataFlows'
import Chat from './pages/Chat'
import Settings from './pages/Settings'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/documents/:id" element={<DocumentDetail />} />
            <Route path="/findings" element={<Findings />} />
            <Route path="/findings/:id" element={<FindingDetail />} />
            <Route path="/remediation" element={<Remediation />} />
            <Route path="/processing-activities" element={<ProcessingActivities />} />
            <Route path="/data-flows" element={<DataFlows />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
