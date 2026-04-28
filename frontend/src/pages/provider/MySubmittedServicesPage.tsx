import { useEffect, useState } from 'react'
import * as providerApi from '../../api/provider'
import { Table } from '../../components/Table'

export function MySubmittedServicesPage() {
  const [records, setRecords] = useState<providerApi.MyServiceRecord[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    providerApi
      .myServices()
      .then(setRecords)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load records'))
  }, [])

  return (
    <div className="card">
      <h2>My Submitted Services</h2>
      <p className="muted">Recent service records you’ve submitted.</p>
      {error ? <div className="alert bad">{error}</div> : null}
      <Table>
        <thead>
          <tr>
            <th>Received</th>
            <th>Date of service</th>
            <th>Member</th>
            <th>Service</th>
            <th>Fee</th>
            <th>Comments</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r.id}>
              <td>{String(r.received_at).replace('T', ' ').slice(0, 19)}</td>
              <td>{r.date_of_service}</td>
              <td>
                {r.member_name} ({r.member_number})
              </td>
              <td>
                {r.service_name} ({r.service_code})
              </td>
              <td>${Number(r.fee).toFixed(2)}</td>
              <td>{r.comments}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  )
}

