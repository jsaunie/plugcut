import { apiFetch } from '@/shared/http'

import type { TokenPair, User } from './types'

export function register(email: string, password: string): Promise<User> {
  return apiFetch<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function login(email: string, password: string): Promise<TokenPair> {
  return apiFetch<TokenPair>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function me(): Promise<User> {
  return apiFetch<User>('/auth/me')
}

export function refresh(refreshToken: string): Promise<TokenPair> {
  return apiFetch<TokenPair>('/auth/refresh', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
}
