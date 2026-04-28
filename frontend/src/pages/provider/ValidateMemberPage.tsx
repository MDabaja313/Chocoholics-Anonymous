import { FormEvent, useState } from 'react'
import * as providerApi from '../../api/provider'

export function ValidateMemberPage() {
  const [memberNumber, setMemberNumber] = useState('')
  const [result, setResult] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setResult(null)
    setBusy(true)
    try {
      const res = await providerApi.validateMember(memberNumber.trim())
      setResult(res.result)
    } catch (err) {
      setResult(err instanceof Error ? err.message : 'Validation failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card">
      <h2>Validate Member</h2>
      <p className="muted">Enter a 9-digit member number to validate eligibility.</p>
      <form onSubmit={onSubmit} className="form" style={{ maxWidth: 520 }}>
        <label>
          Member number
          <input value={memberNumber} onChange={(e) => setMemberNumber(e.target.value)} placeholder="#########" />
        </label>
        <button className="btn primary" disabled={busy}>
          {busy ? 'Validating…' : 'Validate'}
        </button>
      </form>
      {result ? (
        <div className={`alert ${result === 'Validated' ? '' : 'bad'}`} style={{ marginTop: 12 }}>
          {result}
        </div>
      ) : null}
    </div>
  )
}

