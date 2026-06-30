export interface User {
  id: string
  email: string
  created_at: string
  email_verified: boolean
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}
