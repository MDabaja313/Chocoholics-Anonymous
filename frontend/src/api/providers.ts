import { apiFetch } from './client'

export type Provider = {
  id: number
  name: string
  provider_number: string
  street: string
  city: string
  state: string
  zip_code: string
  status: 'active' | 'suspended'
  email?: string | null
  bank_account?: string | null
}

export type ProviderCreate = Omit<Provider, 'id'>
export type ProviderUpdate = Partial<Omit<ProviderCreate, 'provider_number'>>

export function listProviders(q?: string) {
  const qs = q ? `?q=${encodeURIComponent(q)}` : ''
  return apiFetch<Provider[]>(`/api/providers${qs}`)
}

export function createProvider(payload: ProviderCreate) {
  return apiFetch<Provider>('/api/providers', { method: 'POST', body: JSON.stringify(payload) })
}

export function updateProvider(providerNumber: string, payload: ProviderUpdate) {
  return apiFetch<Provider>(`/api/providers/${encodeURIComponent(providerNumber)}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deleteProvider(providerNumber: string) {
  return apiFetch<void>(`/api/providers/${encodeURIComponent(providerNumber)}`, { method: 'DELETE' })
}

