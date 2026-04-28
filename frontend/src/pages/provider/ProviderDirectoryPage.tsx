import { useEffect, useState } from 'react'
import * as servicesApi from '../../api/services'
import { Table } from '../../components/Table'

export function ProviderDirectoryPage() {
  const [services, setServices] = useState<servicesApi.Service[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    servicesApi
      .listServices()
      .then(setServices)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load services'))
  }, [])

  return (
    <div className="card">
      <h2>Provider Directory</h2>
      <p className="muted">Services are listed alphabetically by name.</p>
      {error ? <div className="alert bad">{error}</div> : null}
      <Table>
        <thead>
          <tr>
            <th>Service name</th>
            <th>Code</th>
            <th>Fee</th>
          </tr>
        </thead>
        <tbody>
          {services.map((s) => (
            <tr key={s.code}>
              <td>{s.name}</td>
              <td style={{ fontFamily: 'ui-monospace, Consolas, monospace' }}>{s.code}</td>
              <td>${Number(s.fee).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  )
}

