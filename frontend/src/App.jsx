import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './lib/AuthContext'
import Landing from './pages/Landing'
import SignUp from './pages/SignUp'
import SignIn from './pages/SignIn'
import Dashboard from './pages/Dashboard'
import NewExperiment from './pages/NewExperiment'
import ExperimentView from './pages/ExperimentView'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return (
    <div style={{ minHeight: '100vh', background: '#0a0d0f', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'rgba(232,230,224,0.3)', fontFamily: 'DM Mono', fontSize: 12 }}>
      Loading...
    </div>
  )
  return user ? children : <Navigate to="/signin" />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/signup" element={<SignUp />} />
      <Route path="/signin" element={<SignIn />} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/experiment/new" element={<ProtectedRoute><NewExperiment /></ProtectedRoute>} />
      <Route path="/experiment/:id" element={<ProtectedRoute><ExperimentView /></ProtectedRoute>} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster
          position="top-right"
          toastOptions={{
            style: { background: '#0f1316', color: '#e8e6e0', border: '0.5px solid rgba(255,255,255,0.1)', fontFamily: 'Syne, sans-serif', fontSize: 13 }
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  )
}
