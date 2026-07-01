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
          <UiButton variant="ghost" @click="logout">{{ t('auth.logout') }}</UiButton>
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
.app__head {
  border-bottom: 1px solid var(--line-on-ink);
}
.app__head-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  row-gap: 0.3rem;
  min-height: 72px;
  padding-block: 0.6rem;
}
.app__wordmark {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.4rem;
  letter-spacing: -0.03em;
}
.app__cut {
  color: var(--accent);
}
/* Mobile: the nav drops to its own full-width row, horizontally scrollable. */
.app__nav {
  display: flex;
  gap: 1.4rem;
  order: 3;
  width: 100%;
  margin: 0 calc(-1 * var(--gutter, 1rem));
  padding: 0.2rem var(--gutter, 1rem) 0.1rem;
  overflow-x: auto;
  scrollbar-width: none;
}
.app__nav::-webkit-scrollbar {
  display: none;
}
.app__navlink {
  font-size: 0.95rem;
  color: var(--muted-on-ink);
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
  white-space: nowrap;
}
.app__navlink:hover {
  color: var(--text-on-ink);
}
.app__navlink--active {
  color: var(--text-on-ink);
  border-bottom-color: var(--accent);
}
.app__user {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.app__email {
  display: none;
  font-family: var(--font-mono);
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
@media (min-width: 720px) {
  .app__head-inner {
    flex-wrap: nowrap;
    height: 72px;
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
}
.app__main {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
}
</style>
