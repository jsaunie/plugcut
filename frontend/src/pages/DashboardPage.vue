<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'

import { useAuthStore } from '@/features/auth/store'
import { ApiError } from '@/shared/http'
import { UiButton } from '@/ui'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()

onMounted(async () => {
  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch (err) {
      // Token invalid or expired: drop it and bounce to login.
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
  <div class="dash">
    <header class="dash__head">
      <div class="container dash__head-inner">
        <RouterLink to="/" class="dash__wordmark">
          <span>Plug</span><span class="dash__cut">cut</span>
        </RouterLink>
        <div class="dash__user">
          <span v-if="auth.user" class="dash__email">{{ auth.user.email }}</span>
          <UiButton variant="ghost" @click="logout">{{ t('auth.logout') }}</UiButton>
        </div>
      </div>
    </header>

    <main class="container dash__main">
      <h1 class="dash__title">{{ t('dashboard.title') }}</h1>
      <p class="dash__lead">{{ t('dashboard.lead') }}</p>
      <div class="dash__empty">
        <span class="dash__empty-glyph" aria-hidden="true">✂</span>
        <p>{{ t('dashboard.empty') }}</p>
        <UiButton disabled>{{ t('dashboard.newDeal') }}</UiButton>
      </div>
    </main>
  </div>
</template>

<style scoped>
.dash {
  min-height: 100vh;
}
.dash__head {
  border-bottom: 1px solid var(--line-on-ink);
}
.dash__head-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
}
.dash__wordmark {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.4rem;
  letter-spacing: -0.03em;
}
.dash__cut {
  color: var(--accent);
}
.dash__user {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.dash__email {
  font-family: var(--font-mono);
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.dash__main {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
}
.dash__title {
  font-size: var(--fs-display-lg);
}
.dash__lead {
  margin: 0.8rem 0 2.5rem;
  color: var(--muted-on-ink);
  max-width: 50ch;
}
.dash__empty {
  display: grid;
  justify-items: start;
  gap: 1rem;
  padding: clamp(2rem, 5vw, 3.5rem);
  border: 1px dashed var(--line-on-ink);
  border-radius: var(--radius);
  color: var(--muted-on-ink);
}
.dash__empty-glyph {
  font-size: 1.8rem;
}
</style>
