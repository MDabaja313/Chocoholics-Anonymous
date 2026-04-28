import { apiFetch } from './client'

export function validateMember(member_number: string) {
  return apiFetch<{ result: string }>('/api/provider/validate-member', {
    method: 'POST',
    body: JSON.stringify({ member_number }),
  })
}

export type BillServicePayload = {
  date_of_service: string
  member_number: string
  service_code: string
  comments?: string
  provider_number?: string | null
}

export function billService(payload: BillServicePayload) {
  return apiFetch<{ result: string; fee: string; service_name: string; received_at: string }>(
    '/api/service-records',
    { method: 'POST', body: JSON.stringify(payload) },
  )
}

export type MyServiceRecord = {
  id: number
  received_at: string
  date_of_service: string
  provider_number: string
  provider_name: string
  member_number: string
  member_name: string
  service_code: string
  service_name: string
  fee: string
  comments: string
}

export function myServices() {
  return apiFetch<MyServiceRecord[]>('/api/service-records/mine')
}

