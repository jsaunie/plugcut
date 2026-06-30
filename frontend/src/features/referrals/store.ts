import { defineStore } from 'pinia'

import * as api from './api'
import type { CreateReferralPayload, Referral, ReferralStats } from './types'

interface ReferralsState {
  deals: Referral[]
  stats: ReferralStats | null
  loading: boolean
  loaded: boolean
}

export const useReferralsStore = defineStore('referrals', {
  state: (): ReferralsState => ({
    deals: [],
    stats: null,
    loading: false,
    loaded: false,
  }),
  actions: {
    async fetchAll(): Promise<void> {
      this.loading = true
      try {
        this.deals = await api.listReferrals()
        this.loaded = true
      } finally {
        this.loading = false
      }
    },

    async fetchStats(): Promise<void> {
      this.stats = await api.getStats()
    },

    async create(payload: CreateReferralPayload): Promise<Referral> {
      const deal = await api.createReferral(payload)
      this.deals = [deal, ...this.deals]
      return deal
    },
  },
})
