import { FormEvent, useEffect, useState } from 'react'
import * as servicesApi from '../../api/services'
import { Table } from '../../components/Table'

const empty: servicesApi.ServiceCreate = {
  code: '',
  name: '',
  fee: '0.00',
}

export function ServicesPage() {
  const [items, setItems] = useState<servicesApi.Service[]>([])
  const [q, setQ] = useState('')
  const [form, setForm] = useState<servicesApi.ServiceCreate>({ ...empty })
  const [msg, setMsg] = useState<string | null>(null)

  async function refresh() {
    setMsg(null)
    try {
      setItems(await servicesApi.listServices(q.trim() || undefined))
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Failed to load services')
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
      await servicesApi.createService(form)
      setForm({ ...empty })
      setMsg('Service created.')
      await refresh()
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Create failed')
    }
  }

  async function onDelete(code: string) {
    if (!confirm(`Delete service ${code}?`)) return
    setMsg(null)
    try {
      await servicesApi.deleteService(code)
      setMsg('Service deleted.')
      await refresh()
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Delete failed')
    }
  }

  return (
    <div className="grid2">
      <div className="card">
        <h2>Services / Provider Directory</h2>
        <div className="actions">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search name or code" />
          <button className="btn" onClick={refresh}>
            Search
          </button>
        </div>
        {msg ? <div className={`alert ${msg.includes('failed') || msg.includes('Failed') ? 'bad' : ''}`}>{msg}</div> : null}
        <Table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Code</th>
              <th>Fee</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {items.map((s) => (
              <tr key={s.code}>
                <td>{s.name}</td>
                <td style={{ fontFamily: 'ui-monospace, Consolas, monospace' }}>{s.code}</td>
                <td>${Number(s.fee).toFixed(2)}</td>
                <td>
                  <button className="btn" onClick={() => onDelete(s.code)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>

      <div className="card">
        <h2>Add Service</h2>
        <form className="form" onSubmit={onCreate}>
          <label>
            Service code (6 digits)
            <input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
          </label>
          <label>
            Service name (max 20)
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label>
            Fee (0.00 - 999.99)
            <input value={form.fee} onChange={(e) => setForm({ ...form, fee: e.target.value })} />
          </label>
          <button className="btn primary">Create</button>
        </form>
      </div>
    </div>
  )
}

