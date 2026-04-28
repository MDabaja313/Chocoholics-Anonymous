import { Navigate } from 'react-router-dom'
import { useAuth } from '../app/AuthContext'

export function HomeRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <div className="page"><div className="card">Loading…</div></div>
  if (!user) return <Navigate to="/login" replace />

  if (user.role === 'provider') return <Navigate to="/provider/validate" replace />
  if (user.role === 'manager') return <Navigate to="/manager/members" replace />
  return <Navigate to="/provider/validate" replace />
}

