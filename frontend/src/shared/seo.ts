// Lightweight per-route head management for the SPA (title, description, canonical,
// social tags). The static base tags live in index.html; this localizes/overrides them
// per page on navigation. No dependency.

const BASE_URL = 'https://plugcut.com'

interface SeoOptions {
  title: string
  description?: string
  path?: string
}

function upsertMeta(key: string, content: string, attr: 'name' | 'property' = 'name'): void {
  let el = document.head.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function upsertCanonical(href: string): void {
  let el = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', 'canonical')
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
}

export function useSeo({ title, description, path = '/' }: SeoOptions): void {
  document.title = title
  upsertMeta('og:title', title, 'property')
  upsertMeta('twitter:title', title)
  if (description) {
    upsertMeta('description', description)
    upsertMeta('og:description', description, 'property')
    upsertMeta('twitter:description', description)
  }
  const url = `${BASE_URL}${path}`
  upsertMeta('og:url', url, 'property')
  upsertCanonical(url)
}
