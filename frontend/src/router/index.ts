import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import LandingPage from '@/pages/LandingPage.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'landing', component: LandingPage },
  // Placeholder routes so navigation/CTAs are never dead links. These pages are
  // fleshed out in the next milestones (auth UI, legal documents).
  {
    path: '/inscription',
    name: 'register',
    component: () => import('@/pages/PlaceholderPage.vue'),
    props: { titleKey: 'placeholder.register' },
  },
  {
    path: '/connexion',
    name: 'login',
    component: () => import('@/pages/PlaceholderPage.vue'),
    props: { titleKey: 'placeholder.login' },
  },
  {
    path: '/mentions-legales',
    name: 'legal-notice',
    component: () => import('@/pages/PlaceholderPage.vue'),
    props: { titleKey: 'placeholder.legalNotice' },
  },
  {
    path: '/cgu',
    name: 'terms',
    component: () => import('@/pages/PlaceholderPage.vue'),
    props: { titleKey: 'placeholder.terms' },
  },
  {
    path: '/confidentialite',
    name: 'privacy',
    component: () => import('@/pages/PlaceholderPage.vue'),
    props: { titleKey: 'placeholder.privacy' },
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to) {
    if (to.hash) return { el: to.hash, behavior: 'smooth', top: 80 }
    return { top: 0 }
  },
})
