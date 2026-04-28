import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import * as authApi from '../api/auth'

type AuthState = {
  user: authApi.Me | null
  loading: boolean
  refresh: () => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<authApi.Me | null>(null)
  const [loading, setLoading] = useState(true)

  async function refresh() {
    try {
      const u = await authApi.me()
      setUser(u)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  async function signOut() {
    await authApi.logout().catch(() => {})
    setUser(null)
  }

  useEffect(() => {
    refresh()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const value = useMemo(() => ({ user, loading, refresh, signOut }), [user, loading])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

