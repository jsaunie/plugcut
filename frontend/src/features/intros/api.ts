import { apiFetch } from '@/shared/http'

import type { Intro, IntroInbox } from './types'

export function requestIntro(handle: string, message: string): Promise<{ id: string }> {
  return apiFetch<{ id: string }>(`/profiles/${encodeURIComponent(handle)}/intro`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export function getIntros(): Promise<IntroInbox> {
  return apiFetch<IntroInbox>('/intros')
}

export function respondIntro(id: string, accept: boolean): Promise<Intro> {
  return apiFetch<Intro>(`/intros/${id}/respond`, {
    method: 'POST',
    body: JSON.stringify({ accept }),
  })
}
