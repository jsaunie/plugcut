import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import * as authApi from '../api'
import { useAuthStore } from '../store'

vi.mock('../api', () => ({
  register: vi.fn(),
  login: vi.fn(),
  me: vi.fn(),
}))

const mockedApi = vi.mocked(authApi)

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('is unauthenticated by default', () => {
    expect(useAuthStore().isAuthenticated).toBe(false)
  })

  it('stores tokens and user on login', async () => {
    mockedApi.login.mockResolvedValue({
      access_token: 'access-1',
      refresh_token: 'refresh-1',
      token_type: 'bearer',
    })
    mockedApi.me.mockResolvedValue({
      id: '1',
      email: 'dev@example.com',
      created_at: '2026-01-01T00:00:00Z',
      email_verified: false,
    })

    const store = useAuthStore()
    await store.login('dev@example.com', 'supersecret')

    expect(store.isAuthenticated).toBe(true)
    expect(store.user?.email).toBe('dev@example.com')
    expect(localStorage.getItem('plugcut.access')).toBe('access-1')
  })

  it('registers then logs in', async () => {
    mockedApi.register.mockResolvedValue({
      id: '1',
      email: 'dev@example.com',
      created_at: '2026-01-01T00:00:00Z',
      email_verified: false,
    })
    mockedApi.login.mockResolvedValue({
      access_token: 'a',
      refresh_token: 'r',
      token_type: 'bearer',
    })
    mockedApi.me.mockResolvedValue({
      id: '1',
      email: 'dev@example.com',
      created_at: '2026-01-01T00:00:00Z',
      email_verified: false,
    })

    const store = useAuthStore()
    await store.register('dev@example.com', 'supersecret')

    expect(mockedApi.register).toHaveBeenCalledOnce()
    expect(store.isAuthenticated).toBe(true)
  })

  it('clears everything on logout', () => {
    const store = useAuthStore()
    store.setTokens('a', 'r')
    store.logout()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem('plugcut.access')).toBeNull()
  })
})
