import { i18n } from '@/i18n'

const BASE_URL = '/api/v1'

interface ApiErrorBody {
  error?: { code?: string; message?: string }
}

/** Error carrying the backend's stable error code, for i18n-aware handling. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// Injected by the auth store to avoid a circular import (store -> http -> store).
let getAuthToken: () => string | null = () => null
export function setAuthTokenGetter(getter: () => string | null): void {
  getAuthToken = getter
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  headers.set('Accept-Language', i18n.global.locale.value)
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const token = getAuthToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers })

  if (response.status === 204) return undefined as T
  const data: unknown = await response.json().catch(() => null)

  if (!response.ok) {
    const body = data as ApiErrorBody | null
    throw new ApiError(
      response.status,
      body?.error?.code ?? 'http.error',
      body?.error?.message ?? `HTTP ${response.status}`,
    )
  }
  return data as T
}
