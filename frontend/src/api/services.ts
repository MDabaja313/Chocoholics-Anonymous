import { apiFetch } from './client'

export type Service = {
  id: number
  code: string
  name: string
  fee: string // backend returns as string via Decimal
}

export type ServiceCreate = Omit<Service, 'id'>
export type ServiceUpdate = Partial<Omit<ServiceCreate, 'code'>>

export function listServices(q?: string) {
  const qs = q ? `?q=${encodeURIComponent(q)}` : ''
  return apiFetch<Service[]>(`/api/services${qs}`)
}

export function getServiceByCode(code: string) {
  return apiFetch<Service>(`/api/services/by-code/${encodeURIComponent(code)}`)
}

export function createService(payload: ServiceCreate) {
  return apiFetch<Service>('/api/services', { method: 'POST', body: JSON.stringify(payload) })
}

export function updateService(code: string, payload: ServiceUpdate) {
  return apiFetch<Service>(`/api/services/${encodeURIComponent(code)}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deleteService(code: string) {
  return apiFetch<void>(`/api/services/${encodeURIComponent(code)}`, { method: 'DELETE' })
}

