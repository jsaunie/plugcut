<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'

import { useAuthStore } from '@/features/auth/store'
import { ApiError } from '@/shared/http'
import { UiButton } from '@/ui'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()

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
          <RouterLink to="/app" class="app__navlink" exact-active-class="app__navlink--active">
            {{ t('nav.deals') }}
          </RouterLink>
          <RouterLink
            to="/app/contacts"
            class="app__navlink"
            active-class="app__navlink--active"
          >
            {{ t('nav.contacts') }}
          </RouterLink>
          <RouterLink
            to="/app/reseau"
            class="app__navlink"
            active-class="app__navlink--active"
          >
            {{ t('nav.network') }}
          </RouterLink>
          <RouterLink
            to="/app/intros"
            class="app__navlink"
            active-class="app__navlink--active"
          >
            {{ t('nav.intros') }}
          </RouterLink>
          <RouterLink
            to="/app/profil"
            class="app__navlink"
            active-class="app__navlink--active"
          >
            {{ t('nav.profile') }}
          </RouterLink>
        </nav>
        <div class="app__user">
          <span v-if="auth.user" class="app__email">{{ auth.user.email }}</span>
          <UiButton variant="ghost" size="sm" class="app__logout-text" @click="logout">
            {{ t('auth.logout') }}
          </UiButton>
          <button class="app__logout-icon" :aria-label="t('auth.logout')" @click="logout">
            <svg
              viewBox="0 0 24 24"
              width="19"
              height="19"
              aria-hidden="true"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
          </button>
        </div>
      </div>
    </header>
    <main class="container app__main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
}
/* Sticky, lightly frosted so content scrolls under it without losing the nav. */
.app__head {
  position: sticky;
  top: 0;
  z-index: 20;
  background: color-mix(in srgb, var(--ink) 85%, transparent);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line-on-ink);
}
.app__head-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  row-gap: 0.5rem;
  min-height: 64px;
  padding-block: 0.7rem;
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
/* Mobile: the nav drops to its own full-width row, a horizontally scrollable
   segmented strip; the active tab is a filled pill for a clearer, less basic look. */
.app__nav {
  display: flex;
  gap: 0.3rem;
  order: 3;
  width: 100%;
  margin: 0 calc(-1 * var(--gutter, 1rem));
  padding: 0.1rem var(--gutter, 1rem) 0.15rem;
  overflow-x: auto;
  scrollbar-width: none;
}
.app__nav::-webkit-scrollbar {
  display: none;
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
.app__logout-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-btn, 14px);
  border: 1px solid var(--line-on-ink);
  color: var(--text-on-ink);
  transition:
    border-color var(--dur-fast) ease,
    background var(--dur-fast) ease;
}
.app__logout-icon:hover {
  border-color: var(--text-on-ink);
  background: var(--ink-3);
}
@media (min-width: 720px) {
  .app__head-inner {
    flex-wrap: nowrap;
    height: 72px;
    min-height: 0;
    padding-block: 0;
  }
  .app__nav {
    order: 0;
    width: auto;
    margin: 0 auto 0 2rem;
    padding: 0;
    overflow: visible;
  }
  .app__email {
    display: inline;
  }
  .app__logout-text {
    display: inline-flex;
  }
  .app__logout-icon {
    display: none;
  }
}
.app__main {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
}
</style>
