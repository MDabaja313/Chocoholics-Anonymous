import { FormEvent, useEffect, useState } from 'react'
import * as providersApi from '../../api/providers'
import { Table } from '../../components/Table'

const empty: providersApi.ProviderCreate = {
  name: '',
  provider_number: '',
  street: '',
  city: '',
  state: '',
  zip_code: '',
  status: 'active',
  email: '',
  bank_account: '',
}

export function ProvidersPage() {
  const [items, setItems] = useState<providersApi.Provider[]>([])
  const [q, setQ] = useState('')
  const [form, setForm] = useState<providersApi.ProviderCreate>({ ...empty })
  const [msg, setMsg] = useState<string | null>(null)

  async function refresh() {
    setMsg(null)
    try {
      setItems(await providersApi.listProviders(q.trim() || undefined))
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Failed to load providers')
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
      await providersApi.createProvider({
        ...form,
        email: form.email || null,
        bank_account: form.bank_account || null,
      })
      setForm({ ...empty })
      setMsg('Provider created.')
      await refresh()
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Create failed')
    }
  }

  async function onDelete(providerNumber: string) {
    if (!confirm(`Delete provider ${providerNumber}?`)) return
    setMsg(null)
    try {
      await providersApi.deleteProvider(providerNumber)
      setMsg('Provider deleted.')
      await refresh()
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Delete failed')
    }
  }

  async function onToggleStatus(p: providersApi.Provider) {
    setMsg(null)
    const next = p.status === 'active' ? 'suspended' : 'active'
    try {
      await providersApi.updateProvider(p.provider_number, { status: next })
      setMsg('Status updated.')
      await refresh()
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Update failed')
    }
  }

  return (
    <div className="grid2">
      <div className="card">
        <h2>Providers</h2>
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
              <th>Provider #</th>
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.provider_number}>
                <td>{p.name}</td>
                <td style={{ fontFamily: 'ui-monospace, Consolas, monospace' }}>{p.provider_number}</td>
                <td>{p.status}</td>
                <td style={{ whiteSpace: 'nowrap' }}>
                  <button className="btn" onClick={() => onToggleStatus(p)}>
                    Toggle status
                  </button>{' '}
                  <button className="btn" onClick={() => onDelete(p.provider_number)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>

      <div className="card">
        <h2>Add Provider</h2>
        <form className="form" onSubmit={onCreate}>
          <label>
            Name
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label>
            Provider number (9 digits)
            <input value={form.provider_number} onChange={(e) => setForm({ ...form, provider_number: e.target.value })} />
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
          <div className="row">
            <label>
              Email (optional)
              <input value={form.email ?? ''} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </label>
            <label>
              Bank account (optional)
              <input
                value={form.bank_account ?? ''}
                onChange={(e) => setForm({ ...form, bank_account: e.target.value })}
              />
            </label>
          </div>
          <button className="btn primary">Create</button>
        </form>
      </div>
    </div>
  )
}

