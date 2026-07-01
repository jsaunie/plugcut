import { describe, expect, it } from 'vitest'

import { trustTier, type Reputation } from '../types'

function rep(overrides: Partial<Reputation> = {}): Reputation {
  return {
    sealed_deals: 0,
    completed_deals: 0,
    disputed_deals: 0,
    as_referrer: 0,
    as_placed: 0,
    trust_score: 0,
    has_track_record: false,
    ...overrides,
  }
}

describe('trustTier', () => {
  it('is "none" without a track record', () => {
    expect(trustTier(rep())).toBe('none')
  })

  it('is "emerging" for a low but present score', () => {
    expect(trustTier(rep({ has_track_record: true, trust_score: 20 }))).toBe('emerging')
  })

  it('is "established" from 40', () => {
    expect(trustTier(rep({ has_track_record: true, trust_score: 40 }))).toBe('established')
    expect(trustTier(rep({ has_track_record: true, trust_score: 74 }))).toBe('established')
  })

  it('is "trusted" from 75', () => {
    expect(trustTier(rep({ has_track_record: true, trust_score: 75 }))).toBe('trusted')
    expect(trustTier(rep({ has_track_record: true, trust_score: 100 }))).toBe('trusted')
  })
})
