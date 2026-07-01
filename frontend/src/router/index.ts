import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import { useAuthStore } from '@/features/auth/store'
import LandingPage from '@/pages/LandingPage.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'landing', component: LandingPage },
  {
    path: '/inscription',
    name: 'register',
    component: () => import('@/pages/RegisterPage.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/connexion',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/app',
    name: 'dashboard',
    component: () => import('@/pages/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/app/deals/nouveau',
    name: 'deal-create',
    component: () => import('@/pages/CreateDealPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/app/deals/:id',
    name: 'deal-detail',
    component: () => import('@/pages/DealDetailPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/app/contacts',
    name: 'contacts',
    component: () => import('@/pages/ContactsPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/app/contacts/nouveau',
    name: 'contact-create',
    component: () => import('@/pages/ContactFormPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/app/contacts/:id',
    name: 'contact-edit',
    component: () => import('@/pages/ContactFormPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/app/profil',
    name: 'profile',
    component: () => import('@/pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  // Public reputation page: shareable, no account needed to view.
  {
    path: '/p/:handle',
    name: 'public-profile',
    component: () => import('@/pages/PublicProfilePage.vue'),
  },
  // Public signing page for the placed person (token is the credential, no account).
  {
    path: '/invitation/:token',
    name: 'invitation',
    component: () => import('@/pages/InvitationPage.vue'),
  },
  // Legal documents.
  {
    path: '/mentions-legales',
    name: 'legal-notice',
    component: () => import('@/pages/LegalDocPage.vue'),
    props: { doc: 'notice' },
  },
  {
    path: '/cgu',
    name: 'terms',
    component: () => import('@/pages/LegalDocPage.vue'),
    props: { doc: 'terms' },
  },
  {
    path: '/confidentialite',
    name: 'privacy',
    component: () => import('@/pages/LegalDocPage.vue'),
    props: { doc: 'privacy' },
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

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  return true
})
