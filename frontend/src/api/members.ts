import { apiFetch } from './client'

export type Member = {
  id: number
  name: string
  member_number: string
  street: string
  city: string
  state: string
  zip_code: string
  status: 'active' | 'suspended'
}

export type MemberCreate = Omit<Member, 'id'>
export type MemberUpdate = Partial<Omit<MemberCreate, 'member_number'>>

export function listMembers(q?: string) {
  const qs = q ? `?q=${encodeURIComponent(q)}` : ''
  return apiFetch<Member[]>(`/api/members${qs}`)
}

export function createMember(payload: MemberCreate) {
  return apiFetch<Member>('/api/members', { method: 'POST', body: JSON.stringify(payload) })
}

export function updateMember(memberNumber: string, payload: MemberUpdate) {
  return apiFetch<Member>(`/api/members/${encodeURIComponent(memberNumber)}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deleteMember(memberNumber: string) {
  return apiFetch<void>(`/api/members/${encodeURIComponent(memberNumber)}`, { method: 'DELETE' })
}

