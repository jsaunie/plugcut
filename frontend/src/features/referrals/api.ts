import { apiFetch } from '@/shared/http'

import type { AcceptParty, CreateReferralPayload, Installment, Referral, ReferralDetail } from './types'

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

export function qualifyReferral(id: string): Promise<Referral> {
  return apiFetch<Referral>(`/referrals/${id}/qualify`, { method: 'POST' })
}

export function acceptReferral(id: string, party: AcceptParty): Promise<Referral> {
  return apiFetch<Referral>(`/referrals/${id}/accept`, {
    method: 'POST',
    body: JSON.stringify({ party }),
  })
}

export function activateReferral(id: string): Promise<Referral> {
  return apiFetch<Referral>(`/referrals/${id}/activate`, { method: 'POST' })
}

export function payInstallment(id: string, sequence: number): Promise<Installment> {
  return apiFetch<Installment>(`/referrals/${id}/installments/${sequence}/pay`, {
    method: 'POST',
  })
}

export function getAgreement(id: string): Promise<{ html: string }> {
  return apiFetch<{ html: string }>(`/referrals/${id}/agreement`)
}
