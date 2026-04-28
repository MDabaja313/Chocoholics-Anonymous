import { apiFetch } from './client'

export function suspendMember(memberNumber: string) {
  return apiFetch<{ result: string }>(`/api/acme/suspend-member/${encodeURIComponent(memberNumber)}`, {
    method: 'POST',
  })
}

export function reinstateMember(memberNumber: string) {
  return apiFetch<{ result: string }>(`/api/acme/reinstate-member/${encodeURIComponent(memberNumber)}`, {
    method: 'POST',
  })
}

