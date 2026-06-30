// Returns an i18n key when invalid, else null.

export function nameError(value: string): string | null {
  if (!value.trim()) return 'contacts.errors.nameRequired'
  return null
}

/** Split a comma-separated tags input into a clean array. */
export function parseTags(raw: string): string[] {
  return raw
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}
