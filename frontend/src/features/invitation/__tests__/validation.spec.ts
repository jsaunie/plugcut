import { describe, expect, it } from 'vitest'

import { signatureError } from '../validation'

describe('invitation validation', () => {
  it('requires a non-empty signature name', () => {
    expect(signatureError('')).toBe('invitation.errors.nameRequired')
    expect(signatureError('   ')).toBe('invitation.errors.nameRequired')
    expect(signatureError('Jean Saunie')).toBeNull()
  })
})
