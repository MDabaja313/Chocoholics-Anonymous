import { useEffect, useState } from 'react'
import * as reportsApi from '../../api/reports'
import { Table } from '../../components/Table'

export function ReportsPage() {
  const [msg, setMsg] = useState<string | null>(null)
  const [files, setFiles] = useState<string[]>([])

  async function refreshFiles() {
    const res = await reportsApi.listReportFiles()
    setFiles(res.files)
  }

  useEffect(() => {
    refreshFiles().catch(() => {})
  }, [])

  async function runWeekly() {
    setMsg(null)
    try {
      const res = await reportsApi.runWeeklyReports()
      setMsg(`Generated: ${res.generated.summary_report}, ${res.generated.eft_file} (+ member/provider reports)`)
      await refreshFiles()
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Failed to generate reports')
    }
  }

  return (
    <div className="card">
      <h2>Weekly Accounting Procedure</h2>
      <p className="muted">Generates member reports, provider reports, manager summary, and EFT file.</p>
      <div className="actions">
        <button className="btn primary" onClick={runWeekly}>
          Run Weekly Accounting Procedure
        </button>
        <button className="btn" onClick={() => refreshFiles().catch(() => {})}>
          Refresh file list
        </button>
      </div>
      {msg ? <div className={`alert ${msg.includes('Failed') ? 'bad' : ''}`}>{msg}</div> : null}

      <h3 style={{ marginTop: 16 }}>Generated report files</h3>
      <Table>
        <thead>
          <tr>
            <th>Filename</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {files.map((f) => (
            <tr key={f}>
              <td style={{ fontFamily: 'ui-monospace, Consolas, monospace' }}>{f}</td>
              <td>
                <a className="btn" href={reportsApi.reportDownloadUrl(f)} target="_blank" rel="noreferrer">
                  Download/Open
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  )
}

