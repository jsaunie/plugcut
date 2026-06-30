// Client-side validation mirrors the backend rules (Email value object, 8-char
// minimum). Returns an i18n key so the caller localizes it, or null when valid.

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/
export const MIN_PASSWORD_LENGTH = 8

export function emailError(value: string): string | null {
  const trimmed = value.trim()
  if (!trimmed) return 'auth.errors.emailRequired'
  if (!EMAIL_RE.test(trimmed)) return 'auth.errors.emailInvalid'
  return null
}

export function passwordError(value: string): string | null {
  if (!value) return 'auth.errors.passwordRequired'
  if (value.length < MIN_PASSWORD_LENGTH) return 'auth.errors.passwordTooShort'
  return null
}
