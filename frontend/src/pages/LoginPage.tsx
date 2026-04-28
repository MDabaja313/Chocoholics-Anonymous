import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as authApi from '../api/auth'
import { useAuth } from '../app/AuthContext'

export function LoginPage() {
  const { refresh } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      await authApi.login(username.trim(), password)
      await refresh()
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <div className="card loginCard">
        <h1>ChocAn DPS</h1>
        <p className="muted">Sign in to continue.</p>

        <form onSubmit={onSubmit} className="form">
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </label>
          {error ? <div className="alert bad">{error}</div> : null}
          <button className="btn primary" disabled={busy}>
            {busy ? 'Signing in…' : 'Login'}
          </button>
        </form>

        <div className="muted small" style={{ marginTop: 12 }}>
          Demo: admin/admin123 · provider1/provider123 · manager/manager123
        </div>
      </div>
    </div>
  )
}

