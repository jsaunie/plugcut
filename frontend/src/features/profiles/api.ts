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

export function searchProfiles(skill = '', available = true): Promise<PublicProfile[]> {
  const params = new URLSearchParams()
  if (skill.trim()) params.set('skill', skill.trim())
  if (!available) params.set('available', 'false')
  const query = params.toString()
  return apiFetch<PublicProfile[]>(`/profiles${query ? `?${query}` : ''}`)
}
