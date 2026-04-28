import { FormEvent, useState } from 'react'
import * as providerApi from '../../api/provider'
import * as servicesApi from '../../api/services'
import { useAuth } from '../../app/AuthContext'

export function BillServicePage() {
  const { user } = useAuth()
  const [memberNumber, setMemberNumber] = useState('')
  const [dateOfService, setDateOfService] = useState('')
  const [serviceCode, setServiceCode] = useState('')
  const [comments, setComments] = useState('')

  const [verified, setVerified] = useState<{ name: string; fee: string } | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [busyVerify, setBusyVerify] = useState(false)
  const [busyBill, setBusyBill] = useState(false)

  async function onVerify(e: FormEvent) {
    e.preventDefault()
    setMessage(null)
    setVerified(null)
    setBusyVerify(true)
    try {
      const svc = await servicesApi.getServiceByCode(serviceCode.trim())
      setVerified({ name: svc.name, fee: svc.fee })
      setMessage(`Verified: ${svc.name} — $${Number(svc.fee).toFixed(2)}`)
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Service lookup failed')
    } finally {
      setBusyVerify(false)
    }
  }

  async function onBill(e: FormEvent) {
    e.preventDefault()
    setMessage(null)
    if (!verified) {
      setMessage('Verify a valid service code first.')
      return
    }
    setBusyBill(true)
    try {
      const res = await providerApi.billService({
        member_number: memberNumber.trim(),
        date_of_service: dateOfService.trim(),
        service_code: serviceCode.trim(),
        comments: comments.trim(),
      })
      setMessage(`Service recorded. Fee: $${Number(res.fee).toFixed(2)}. Received: ${res.received_at}`)
      setVerified(null)
      setComments('')
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Billing failed')
    } finally {
      setBusyBill(false)
    }
  }

  return (
    <div className="card">
      <h2>Bill Service</h2>
      <p className="muted">
        Provider is automatically taken from your login session
        {user?.provider_number ? ` (${user.provider_number})` : ''}.
      </p>

      <form className="form" onSubmit={onBill} style={{ maxWidth: 680 }}>
        <div className="row">
          <label>
            Member number
            <input value={memberNumber} onChange={(e) => setMemberNumber(e.target.value)} placeholder="#########" />
          </label>
          <label>
            Date of service (MM-DD-YYYY)
            <input value={dateOfService} onChange={(e) => setDateOfService(e.target.value)} placeholder="MM-DD-YYYY" />
          </label>
        </div>

        <div className="row">
          <label>
            Service code (6 digits)
            <input value={serviceCode} onChange={(e) => setServiceCode(e.target.value)} placeholder="######" />
          </label>
          <label>
            Comments (optional, max 100)
            <input value={comments} onChange={(e) => setComments(e.target.value)} maxLength={100} />
          </label>
        </div>

        <div className="actions">
          <button className="btn" onClick={onVerify} disabled={busyVerify}>
            {busyVerify ? 'Verifying…' : 'Verify service code'}
          </button>
          <button className="btn primary" type="submit" disabled={busyBill || !verified}>
            {busyBill ? 'Submitting…' : 'Confirm & bill'}
          </button>
        </div>

        {verified ? (
          <div className="alert" style={{ marginTop: 10 }}>
            Confirm billing: <strong>{verified.name}</strong> — ${Number(verified.fee).toFixed(2)}
          </div>
        ) : null}

        {message ? <div className={`alert ${message.startsWith('Service recorded') ? '' : 'bad'}`}>{message}</div> : null}
      </form>
    </div>
  )
}

