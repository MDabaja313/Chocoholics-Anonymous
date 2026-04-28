export type ApiError = {
  detail?: string
  result?: string
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const res = await fetch(path, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
  })

  if (!res.ok) {
    const data = (await res.json().catch(() => ({}))) as ApiError
    const message = data.detail || data.result || `Request failed (${res.status})`
    throw new Error(message)
  }

  // 204 no content
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

