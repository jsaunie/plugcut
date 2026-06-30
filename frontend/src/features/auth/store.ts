import { defineStore } from 'pinia'

import * as authApi from './api'
import type { User } from './types'

const ACCESS_KEY = 'plugcut.access'
const REFRESH_KEY = 'plugcut.refresh'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: User | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: localStorage.getItem(ACCESS_KEY),
    refreshToken: localStorage.getItem(REFRESH_KEY),
    user: null,
  }),
  getters: {
    isAuthenticated: (state): boolean => Boolean(state.accessToken),
  },
  actions: {
    setTokens(access: string, refresh: string): void {
      this.accessToken = access
      this.refreshToken = refresh
      localStorage.setItem(ACCESS_KEY, access)
      localStorage.setItem(REFRESH_KEY, refresh)
    },

    async register(email: string, password: string): Promise<void> {
      await authApi.register(email, password)
      await this.login(email, password)
    },

    async login(email: string, password: string): Promise<void> {
      const tokens = await authApi.login(email, password)
      this.setTokens(tokens.access_token, tokens.refresh_token)
      await this.fetchMe()
    },

    async fetchMe(): Promise<void> {
      this.user = await authApi.me()
    },

    logout(): void {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem(ACCESS_KEY)
      localStorage.removeItem(REFRESH_KEY)
    },
  },
})
