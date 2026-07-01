export interface Reputation {
  sealed_deals: number
  completed_deals: number
  disputed_deals: number
  as_referrer: number
  as_placed: number
  trust_score: number
  has_track_record: boolean
}

export type TrustTier = 'none' | 'emerging' | 'established' | 'trusted'

/** Map a reputation to a trust tier. Pure and deterministic (mirrors the backend
 *  scoring intent), so the UI never invents its own thresholds ad hoc. */
export function trustTier(reputation: Reputation): TrustTier {
  if (!reputation.has_track_record) return 'none'
  if (reputation.trust_score >= 75) return 'trusted'
  if (reputation.trust_score >= 40) return 'established'
  return 'emerging'
}
