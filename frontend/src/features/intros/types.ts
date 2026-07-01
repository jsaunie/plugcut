export interface IntroCounterpart {
  handle: string
  display_name: string
}

export interface Intro {
  id: string
  message: string
  status: 'pending' | 'accepted' | 'declined'
  created_at: string
  responded_at: string | null
  counterpart: IntroCounterpart | null
}

export interface IntroInbox {
  inbound: Intro[]
  outbound: Intro[]
}
