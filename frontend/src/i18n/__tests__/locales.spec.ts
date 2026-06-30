import { describe, expect, it } from 'vitest'

import { i18n } from '../index'
import en from '../locales/en.json'
import fr from '../locales/fr.json'

const t = i18n.global.t

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

  // Regression: the dashboard deal count read "1 deals, 0 actifs". French treats
  // 0 and 1 as singular; English pluralises 0 but not the "active" adjective.
  it('pluralises the deal count per locale grammar', () => {
    expect(t('stats.dealsCount', 1, { locale: 'fr' })).toBe('1 deal')
    expect(t('stats.dealsCount', 0, { locale: 'fr' })).toBe('0 deal')
    expect(t('stats.dealsCount', 2, { locale: 'fr' })).toBe('2 deals')
    expect(t('stats.activeCount', 1, { locale: 'fr' })).toBe('1 actif')
    expect(t('stats.activeCount', 3, { locale: 'fr' })).toBe('3 actifs')

    expect(t('stats.dealsCount', 1, { locale: 'en' })).toBe('1 deal')
    expect(t('stats.dealsCount', 0, { locale: 'en' })).toBe('0 deals')
    expect(t('stats.activeCount', 2, { locale: 'en' })).toBe('2 active')
  })
})
