<script setup lang="ts">
import { RouterLink } from 'vue-router'

import LangSwitch from '@/components/shared/LangSwitch.vue'

defineProps<{ titleKey: string }>()
</script>

<template>
  <div class="ph">
    <div class="ph__top container">
      <RouterLink to="/" class="ph__wordmark">
        <span>Plug</span><span class="ph__cut">cut</span>
      </RouterLink>
      <LangSwitch />
    </div>

    <main class="ph__main container">
      <span class="ph__scissors" aria-hidden="true">✂</span>
      <h1 class="ph__title">{{ $t(titleKey) }}</h1>
      <p class="ph__soon">{{ $t('placeholder.soon') }}</p>
      <RouterLink to="/" class="btn btn--accent">← {{ $t('placeholder.back') }}</RouterLink>
    </main>
  </div>
</template>

<style scoped>
.ph {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.ph__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1.5rem;
}
.ph__wordmark {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.4rem;
  letter-spacing: -0.03em;
}
.ph__cut {
  color: var(--accent);
}
.ph__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 1.2rem;
}
.ph__scissors {
  font-size: 2.5rem;
  opacity: 0.5;
}
.ph__title {
  font-size: clamp(2.2rem, 7vw, 4rem);
}
.ph__soon {
  color: var(--muted-on-ink);
  margin-bottom: 0.8rem;
}
</style>
