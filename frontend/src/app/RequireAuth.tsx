import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

export function RequireAuth() {
  const { user, loading } = useAuth()
  const loc = useLocation()

  if (loading) return <div className="page"><div className="card">Loading…</div></div>
  if (!user) return <Navigate to="/login" replace state={{ from: loc.pathname }} />
  return <Outlet />
}

export function RequireRole({ allow }: { allow: Array<'provider' | 'manager' | 'admin'> }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="page"><div className="card">Loading…</div></div>
  if (!user) return <Navigate to="/login" replace />
  if (!allow.includes(user.role)) return <Navigate to="/" replace />
  return <Outlet />
}

