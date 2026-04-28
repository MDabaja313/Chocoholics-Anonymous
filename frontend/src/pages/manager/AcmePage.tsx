import { FormEvent, useState } from 'react'
import * as acmeApi from '../../api/acme'

export function AcmePage() {
  const [memberNumber, setMemberNumber] = useState('')
  const [msg, setMsg] = useState<string | null>(null)

  async function suspend(e: FormEvent) {
    e.preventDefault()
    setMsg(null)
    try {
      await acmeApi.suspendMember(memberNumber.trim())
      setMsg('Member suspended.')
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Failed to suspend')
    }
  }

  async function reinstate(e: FormEvent) {
    e.preventDefault()
    setMsg(null)
    try {
      await acmeApi.reinstateMember(memberNumber.trim())
      setMsg('Member reinstated.')
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Failed to reinstate')
    }
  }

  return (
    <div className="card">
      <h2>Acme Accounting Simulation</h2>
      <p className="muted">Simulate an outside accounting service updating member payment status.</p>
      <form className="form" style={{ maxWidth: 520 }}>
        <label>
          Member number (9 digits)
          <input value={memberNumber} onChange={(e) => setMemberNumber(e.target.value)} placeholder="#########" />
        </label>
        <div className="actions">
          <button className="btn" onClick={suspend}>
            Mark suspended
          </button>
          <button className="btn primary" onClick={reinstate}>
            Reinstate active
          </button>
        </div>
      </form>
      {msg ? <div className={`alert ${msg.includes('Failed') ? 'bad' : ''}`}>{msg}</div> : null}
    </div>
  )
}

