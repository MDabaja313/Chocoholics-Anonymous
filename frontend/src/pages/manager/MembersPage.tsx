import { FormEvent, useEffect, useState } from 'react'
import * as membersApi from '../../api/members'
import { Table } from '../../components/Table'

const empty: membersApi.MemberCreate = {
  name: '',
  member_number: '',
  street: '',
  city: '',
  state: '',
  zip_code: '',
  status: 'active',
}

export function MembersPage() {
  const [items, setItems] = useState<membersApi.Member[]>([])
  const [q, setQ] = useState('')
  const [form, setForm] = useState<membersApi.MemberCreate>({ ...empty })
  const [msg, setMsg] = useState<string | null>(null)

  async function refresh() {
    setMsg(null)
    try {
      setItems(await membersApi.listMembers(q.trim() || undefined))
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Failed to load members')
    }
  }

  useEffect(() => {
    refresh()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function onCreate(e: FormEvent) {
    e.preventDefault()
    setMsg(null)
    try {
      await membersApi.createMember(form)
      setForm({ ...empty })
      setMsg('Member created.')
      await refresh()
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Create failed')
    }
  }

  async function onDelete(memberNumber: string) {
    if (!confirm(`Delete member ${memberNumber}?`)) return
    setMsg(null)
    try {
      await membersApi.deleteMember(memberNumber)
      setMsg('Member deleted.')
      await refresh()
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Delete failed')
    }
  }

  async function onToggleStatus(m: membersApi.Member) {
    setMsg(null)
    const next = m.status === 'active' ? 'suspended' : 'active'
    try {
      await membersApi.updateMember(m.member_number, { status: next })
      setMsg('Status updated.')
      await refresh()
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Update failed')
    }
  }

  return (
    <div className="grid2">
      <div className="card">
        <h2>Members</h2>
        <div className="actions">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search name or number" />
          <button className="btn" onClick={refresh}>
            Search
          </button>
        </div>
        {msg ? <div className={`alert ${msg.includes('failed') || msg.includes('Failed') ? 'bad' : ''}`}>{msg}</div> : null}
        <Table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Member #</th>
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {items.map((m) => (
              <tr key={m.member_number}>
                <td>{m.name}</td>
                <td style={{ fontFamily: 'ui-monospace, Consolas, monospace' }}>{m.member_number}</td>
                <td>{m.status}</td>
                <td style={{ whiteSpace: 'nowrap' }}>
                  <button className="btn" onClick={() => onToggleStatus(m)}>
                    Toggle status
                  </button>{' '}
                  <button className="btn" onClick={() => onDelete(m.member_number)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>

      <div className="card">
        <h2>Add Member</h2>
        <form className="form" onSubmit={onCreate}>
          <label>
            Name
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label>
            Member number (9 digits)
            <input value={form.member_number} onChange={(e) => setForm({ ...form, member_number: e.target.value })} />
          </label>
          <label>
            Street
            <input value={form.street} onChange={(e) => setForm({ ...form, street: e.target.value })} />
          </label>
          <div className="row">
            <label>
              City
              <input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
            </label>
            <label>
              State
              <input value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} />
            </label>
          </div>
          <div className="row">
            <label>
              ZIP
              <input value={form.zip_code} onChange={(e) => setForm({ ...form, zip_code: e.target.value })} />
            </label>
            <label>
              Status
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as any })}>
                <option value="active">active</option>
                <option value="suspended">suspended</option>
              </select>
            </label>
          </div>
          <button className="btn primary">Create</button>
        </form>
      </div>
    </div>
  )
}

