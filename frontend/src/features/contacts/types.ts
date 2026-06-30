export type ContactKind = 'person' | 'company'

export interface Contact {
  id: string
  full_name: string
  kind: ContactKind
  headline: string
  email: string | null
  phone: string | null
  linkedin_url: string | null
  company: string | null
  location: string | null
  tags: string[]
  notes: string
  source: string
  created_at: string
  updated_at: string
}

export interface ContactSuggestion {
  full_name: string
  headline: string
  linkedin_url: string | null
  notes: string
  source: string
}

export interface ContactInput {
  full_name: string
  kind: ContactKind
  headline: string
  email: string | null
  phone: string | null
  linkedin_url: string | null
  company: string | null
  location: string | null
  tags: string[]
  notes: string
}
