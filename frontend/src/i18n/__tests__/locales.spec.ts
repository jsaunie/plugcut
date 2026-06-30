import { describe, expect, it } from 'vitest'

import en from '../locales/en.json'
import fr from '../locales/fr.json'

function keyPaths(value: unknown, prefix = ''): string[] {
  if (Array.isArray(value)) {
    return value.flatMap((item, index) => keyPaths(item, `${prefix}[${index}]`))
  }
  if (value && typeof value === 'object') {
    return Object.entries(value as Record<string, unknown>).flatMap(([key, child]) =>
      keyPaths(child, prefix ? `${prefix}.${key}` : key),
    )
  }
  return [prefix]
}

function collectStrings(value: unknown): string[] {
  if (typeof value === 'string') return [value]
  if (Array.isArray(value)) return value.flatMap(collectStrings)
  if (value && typeof value === 'object') {
    return Object.values(value as Record<string, unknown>).flatMap(collectStrings)
  }
  return []
}

describe('i18n locales', () => {
  it('fr and en have identical key structure (no missing translations)', () => {
    expect(keyPaths(fr).sort()).toEqual(keyPaths(en).sort())
  })

  it('contain no em dashes in user-facing copy', () => {
    for (const messages of [fr, en]) {
      for (const text of collectStrings(messages)) {
        expect(text).not.toContain('—')
      }
    }
  })
})
