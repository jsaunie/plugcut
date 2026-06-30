export interface Referral {
  id: string
  placed_person_email: string
  client_reference: string
  daily_rate: number
  currency: string
  commission_rate: number
  duration_months: number
  status: string
  attribution_hash: string | null
  created_at: string
  monthly_expected: number
  total_expected: number
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
