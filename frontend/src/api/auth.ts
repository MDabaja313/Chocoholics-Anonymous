import { apiFetch } from './client'

export type Me = {
  username: string
  role: 'provider' | 'manager' | 'admin'
  provider_number?: string | null
  provider_name?: string | null
}

export async function login(username: string, password: string) {
  return apiFetch<{ result: string }>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export async function logout() {
  return apiFetch<{ result: string }>('/api/auth/logout', { method: 'POST' })
}

export async function me() {
  return apiFetch<Me>('/api/auth/me')
}

