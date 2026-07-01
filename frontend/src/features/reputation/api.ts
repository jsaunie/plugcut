import { apiFetch } from '@/shared/http'

import type { Reputation } from './types'

export function getMyReputation(): Promise<Reputation> {
  return apiFetch<Reputation>('/reputation/me')
}
