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
  align-items: center;
  justify-content: space-between;
  height: 72px;
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
.app__nav {
  display: none;
  gap: 1.4rem;
  margin-right: auto;
  margin-left: 2rem;
}
.app__navlink {
  font-size: 0.95rem;
  color: var(--muted-on-ink);
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
}
.app__navlink:hover {
  color: var(--text-on-ink);
}
.app__navlink--active {
  color: var(--text-on-ink);
  border-bottom-color: var(--accent);
}
@media (min-width: 720px) {
  .app__nav {
    display: flex;
  }
}
.app__user {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.app__email {
  font-family: var(--font-mono);
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.app__main {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
}
</style>
