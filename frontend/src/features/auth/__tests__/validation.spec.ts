import { describe, expect, it } from 'vitest'

import { emailError, passwordError } from '../validation'

describe('auth validation', () => {
  it('flags empty and malformed emails, accepts valid ones', () => {
    expect(emailError('')).toBe('auth.errors.emailRequired')
    expect(emailError('nope')).toBe('auth.errors.emailInvalid')
    expect(emailError('  Dev@Example.com ')).toBeNull()
  })

  it('enforces the minimum password length', () => {
    expect(passwordError('')).toBe('auth.errors.passwordRequired')
    expect(passwordError('short')).toBe('auth.errors.passwordTooShort')
    expect(passwordError('supersecret')).toBeNull()
  })
})
