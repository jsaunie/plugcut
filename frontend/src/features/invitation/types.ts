export interface PublicReferral {
  referrer_email: string
  placed_person_email: string
  client_reference: string
  daily_rate: number
  currency: string
  commission_rate: number
  duration_months: number
  monthly_expected: number
  total_expected: number
  status: string
  referrer_signed: boolean
  placed_signed: boolean
  attribution_hash: string | null
}
