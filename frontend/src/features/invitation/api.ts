import { apiFetch } from '@/shared/http'

import type { PublicReferral } from './types'

export function getInvitation(token: string): Promise<PublicReferral> {
  return apiFetch<PublicReferral>(`/invitations/${token}`)
}

export function signInvitation(token: string, signature: string): Promise<PublicReferral> {
  return apiFetch<PublicReferral>(`/invitations/${token}/accept`, {
    method: 'POST',
    body: JSON.stringify({ signature }),
  })
}
