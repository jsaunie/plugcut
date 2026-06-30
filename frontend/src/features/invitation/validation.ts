// Signature is a typed full name. Returns an i18n key when invalid, else null.

export function signatureError(value: string): string | null {
  if (!value.trim()) return 'invitation.errors.nameRequired'
  return null
}
