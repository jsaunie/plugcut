import { defineStore } from 'pinia'

import * as api from './api'
import type { CreateReferralPayload, Referral } from './types'

interface ReferralsState {
  deals: Referral[]
  loading: boolean
  loaded: boolean
}

export const useReferralsStore = defineStore('referrals', {
  state: (): ReferralsState => ({
    deals: [],
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

    async create(payload: CreateReferralPayload): Promise<Referral> {
      const deal = await api.createReferral(payload)
      this.deals = [deal, ...this.deals]
      return deal
    },
  },
})
