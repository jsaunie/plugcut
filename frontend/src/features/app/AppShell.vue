<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/features/auth/store'
import { ApiError } from '@/shared/http'
import { UiButton } from '@/ui'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const menuOpen = ref(false)

// Close the drawer whenever the route changes (a link was tapped).
watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false
  },
)

const navItems = [
  { to: '/app', key: 'deals', exact: true },
  { to: '/app/contacts', key: 'contacts', exact: false },
  { to: '/app/reseau', key: 'network', exact: false },
  { to: '/app/intros', key: 'intros', exact: false },
  { to: '/app/profil', key: 'profile', exact: false },
  { to: '/app/parametres', key: 'settings', exact: false },
]

onMounted(async () => {
  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch (err) {
      if (err instanceof ApiError) {
        auth.logout()
        await router.push('/connexion')
      }
    }
  }
})

function logout(): void {
  menuOpen.value = false
  auth.logout()
  router.push('/')
}
</script>

<template>
  <div class="app">
    <header class="app__head">
      <div class="container app__head-inner">
        <RouterLink to="/app" class="app__wordmark">
          <span>Plug</span><span class="app__cut">cut</span>
        </RouterLink>

        <nav class="app__nav">
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="app__navlink"
            :active-class="item.exact ? '' : 'app__navlink--active'"
            :exact-active-class="item.exact ? 'app__navlink--active' : ''"
          >
            {{ t(`nav.${item.key}`) }}
          </RouterLink>
        </nav>

        <div class="app__user">
          <span v-if="auth.user" class="app__email">{{ auth.user.email }}</span>
          <UiButton variant="ghost" size="sm" class="app__logout-text" @click="logout">
            {{ t('auth.logout') }}
          </UiButton>
          <button
            class="app__burger"
            :aria-label="t('nav.menu')"
            :aria-expanded="menuOpen"
            @click="menuOpen = !menuOpen"
          >
            <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
              <path
                v-if="!menuOpen"
                d="M4 7h16M4 12h16M4 17h16"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
              <path
                v-else
                d="M6 6l12 12M18 6L6 18"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>
      </div>
    </header>

    <Transition name="drawer">
      <nav v-if="menuOpen" class="app__drawer" aria-label="Menu">
        <span class="app__drawer-label">{{ t('nav.menu') }}</span>
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="app__drawer-link"
          :active-class="item.exact ? '' : 'app__drawer-link--active'"
          :exact-active-class="item.exact ? 'app__drawer-link--active' : ''"
        >
          {{ t(`nav.${item.key}`) }}
        </RouterLink>
        <button class="app__drawer-logout" @click="logout">
          {{ t('auth.logout') }}
        </button>
      </nav>
    </Transition>
    <Transition name="fade">
      <div v-if="menuOpen" class="app__backdrop" @click="menuOpen = false" />
    </Transition>

    <main class="container app__main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
}
/* Sticky, lightly frosted so content scrolls under it. */
.app__head {
  position: sticky;
  top: 0;
  z-index: 30;
  background: color-mix(in srgb, var(--ink) 85%, transparent);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line-on-ink);
}
.app__head-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}
.app__wordmark {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.35rem;
  letter-spacing: -0.03em;
}
.app__cut {
  color: var(--accent);
}
/* Desktop inline nav (hidden on mobile, replaced by the burger drawer). */
.app__nav {
  display: none;
  gap: 0.3rem;
  margin: 0 auto 0 2rem;
}
.app__navlink {
  font-size: 0.92rem;
  font-weight: 500;
  color: var(--muted-on-ink);
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius-pill);
  white-space: nowrap;
  transition:
    color var(--dur-fast) ease,
    background var(--dur-fast) ease;
}
.app__navlink:hover {
  color: var(--text-on-ink);
  background: var(--ink-3);
}
.app__navlink--active,
.app__navlink--active:hover {
  color: var(--accent-ink);
  background: var(--accent);
}
.app__user {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.app__email {
  display: none;
  font-family: var(--font-mono);
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.app__logout-text {
  display: none;
}
/* Burger: mobile only. */
.app__burger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: var(--radius-btn, 14px);
  border: 1px solid var(--line-on-ink);
  color: var(--text-on-ink);
  transition:
    border-color var(--dur-fast) ease,
    background var(--dur-fast) ease;
}
.app__burger:hover {
  border-color: var(--text-on-ink);
  background: var(--ink-3);
}

/* ---- Mobile drawer ---- */
.app__backdrop {
  position: fixed;
  inset: 0;
  background: color-mix(in srgb, var(--solid) 45%, transparent);
  z-index: 40;
}
.app__drawer {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(82vw, 320px);
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 1.4rem 1.2rem calc(1.4rem + env(safe-area-inset-bottom));
  background: var(--ink-2);
  border-left: 1px solid var(--line-on-ink);
  box-shadow: -24px 0 60px -24px rgba(0, 0, 0, 0.3);
}
.app__drawer-label {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: var(--muted-on-ink);
  margin-bottom: 0.8rem;
}
.app__drawer-link {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-on-ink);
  padding: 0.85rem 0.9rem;
  border-radius: var(--radius);
  transition: background var(--dur-fast) ease;
}
.app__drawer-link:hover {
  background: var(--ink-3);
}
.app__drawer-link--active {
  color: var(--accent-ink);
  background: var(--accent);
}
.app__drawer-logout {
  margin-top: auto;
  text-align: left;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-on-ink);
  padding: 0.85rem 0.9rem;
  border-radius: var(--radius);
  border: 1px solid var(--line-on-ink);
}
.app__drawer-logout:hover {
  background: var(--ink-3);
}

.drawer-enter-active,
.drawer-leave-active {
  transition: transform var(--dur) cubic-bezier(0.22, 1, 0.36, 1);
}
.drawer-enter-from,
.drawer-leave-to {
  transform: translateX(100%);
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--dur) ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (min-width: 720px) {
  .app__nav {
    display: flex;
  }
  .app__email {
    display: inline;
  }
  .app__logout-text {
    display: inline-flex;
  }
  .app__burger,
  .app__drawer,
  .app__backdrop {
    display: none;
  }
}
.app__main {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
}
</style>
