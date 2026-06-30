import { apiFetch } from '@/shared/http'

import type { CreateReferralPayload, Referral, ReferralDetail } from './types'

export function listReferrals(): Promise<Referral[]> {
  return apiFetch<Referral[]>('/referrals')
}

export function createReferral(payload: CreateReferralPayload): Promise<Referral> {
  return apiFetch<Referral>('/referrals', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getReferral(id: string): Promise<ReferralDetail> {
  return apiFetch<ReferralDetail>(`/referrals/${id}`)
}
