import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import * as api from '../api'
import { useReferralsStore } from '../store'
import type { Referral } from '../types'

vi.mock('../api', () => ({
  listReferrals: vi.fn(),
  createReferral: vi.fn(),
  getReferral: vi.fn(),
}))

const mockedApi = vi.mocked(api)

function makeDeal(id: string): Referral {
  return {
    id,
    placed_person_email: 'dev@example.com',
    client_reference: 'ACME',
    daily_rate: 500,
    currency: 'EUR',
    commission_rate: 10,
    duration_months: 12,
    status: 'sent',
    attribution_hash: null,
    created_at: '2026-01-01T00:00:00Z',
    monthly_expected: 1000,
    total_expected: 12000,
  }
}

describe('referrals store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('loads deals and marks loaded', async () => {
    mockedApi.listReferrals.mockResolvedValue([makeDeal('1')])
    const store = useReferralsStore()
    await store.fetchAll()
    expect(store.deals).toHaveLength(1)
    expect(store.loaded).toBe(true)
    expect(store.loading).toBe(false)
  })

  it('prepends a newly created deal', async () => {
    mockedApi.createReferral.mockResolvedValue(makeDeal('2'))
    const store = useReferralsStore()
    store.deals = [makeDeal('1')]
    const created = await store.create({
      placed_person_email: 'dev@example.com',
      client_reference: 'X',
      daily_rate: 500,
      commission_rate: 10,
      duration_months: 12,
      days_per_period: 20,
    })
    expect(created.id).toBe('2')
    expect(store.deals[0].id).toBe('2')
    expect(store.deals).toHaveLength(2)
  })
})
