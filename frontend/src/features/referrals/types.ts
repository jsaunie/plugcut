export interface Referral {
  id: string
  placed_person_email: string
  client_reference: string
  daily_rate: number
  currency: string
  commission_rate: number
  duration_months: number
  status: string
  role: 'referrer' | 'placed'
  accepted_by_referrer: boolean
  accepted_by_placed: boolean
  invitation_token: string | null
  attribution_hash: string | null
  created_at: string
  monthly_expected: number
  total_expected: number
  dispute_reason?: string | null
  disputed_at?: string | null
}

export type AcceptParty = 'referrer' | 'placed'

export interface TimelineEntry {
  type: string
  at: string
  detail: string
}

export interface ReferralStats {
  total_deals: number
  active_deals: number
  pipeline_expected: number
  monthly_run_rate: number
  collected: number
  outstanding: number
  overdue: number
  currency: string
}

export interface Installment {
  sequence: number
  period_start: string
  period_end: string
  due_date: string
  expected_amount: number
  status: string
}

export interface ReferralDetail extends Referral {
  schedule: Installment[]
}

export interface CreateReferralPayload {
  placed_person_email: string
  client_reference: string
  daily_rate: number
  commission_rate: number
  duration_months: number
  days_per_period: number
  currency?: string
}
