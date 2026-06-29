<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { setLocale, type AppLocale } from '@/i18n'

const { locale } = useI18n()

function choose(next: AppLocale) {
  setLocale(next)
}
</script>

<template>
  <div class="lang" role="group" aria-label="Language">
    <button
      v-for="code in (['fr', 'en'] as const)"
      :key="code"
      class="lang__btn"
      :class="{ 'lang__btn--active': locale === code }"
      type="button"
      @click="choose(code)"
    >
      {{ $t(`lang.${code}`) }}
    </button>
  </div>
</template>

<style scoped>
.lang {
  display: inline-flex;
  align-items: center;
  gap: 0.15rem;
  padding: 0.2rem;
  border: 1px solid var(--line-on-ink);
  border-radius: 999px;
  font-family: var(--font-mono);
  font-size: 0.72rem;
}
.lang__btn {
  padding: 0.28rem 0.6rem;
  border-radius: 999px;
  color: var(--muted-on-ink);
  letter-spacing: 0.05em;
  transition:
    color 0.15s ease,
    background 0.15s ease;
}
.lang__btn--active {
  background: var(--accent);
  color: var(--accent-ink);
}
</style>
