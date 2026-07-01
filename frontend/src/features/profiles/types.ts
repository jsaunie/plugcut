import type { Reputation } from '@/features/reputation/types'

export interface Profile {
  id: string
  handle: string
  display_name: string
  headline: string
  skills: string[]
  bio: string
  available: boolean
  created_at: string
  updated_at: string
}

export interface ProfileUpsert {
  handle: string
  display_name: string
  headline: string
  skills: string[]
  bio: string
  available: boolean
}

export interface PublicProfile {
  profile: Profile
  reputation: Reputation
}
