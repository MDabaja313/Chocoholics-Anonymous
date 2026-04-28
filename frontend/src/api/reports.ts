import { apiFetch } from './client'

export function runWeeklyReports() {
  return apiFetch<{
    result: string
    generated: {
      member_reports: string[]
      provider_reports: string[]
      summary_report: string
      eft_file: string
    }
  }>('/api/reports/run-weekly', { method: 'POST' })
}

export function listReportFiles() {
  return apiFetch<{ files: string[] }>('/api/reports/files')
}

export function reportDownloadUrl(filename: string) {
  return `/api/reports/files/${encodeURIComponent(filename)}`
}

