import { createI18n } from 'vue-i18n'

import en from './locales/en.json'
import fr from './locales/fr.json'

export type AppLocale = 'fr' | 'en'

const STORAGE_KEY = 'plugcut.locale'

function detectLocale(): AppLocale {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'fr' || stored === 'en') return stored
  return navigator.language.startsWith('en') ? 'en' : 'fr'
}

export const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: 'fr',
  messages: { fr, en },
  // French treats 0 and 1 as singular (0 deal, 1 deal, 2 deals). The default
  // rule pluralises 0, which reads wrong in FR.
  pluralRules: {
    fr: (choice: number) => (choice <= 1 ? 0 : 1),
  },
})

export function setLocale(locale: AppLocale): void {
  i18n.global.locale.value = locale
  localStorage.setItem(STORAGE_KEY, locale)
  document.documentElement.lang = locale
}
