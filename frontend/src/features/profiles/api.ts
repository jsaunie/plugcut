import { apiFetch } from '@/shared/http'

import type { Profile, ProfileUpsert, PublicProfile } from './types'

export function getMyProfile(): Promise<Profile> {
  return apiFetch<Profile>('/profile/me')
}

export function upsertMyProfile(data: ProfileUpsert): Promise<Profile> {
  return apiFetch<Profile>('/profile/me', {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export function getPublicProfile(handle: string): Promise<PublicProfile> {
  return apiFetch<PublicProfile>(`/profiles/${encodeURIComponent(handle)}`)
}
