<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import LangSwitch from '@/components/shared/LangSwitch.vue'

const { t } = useI18n()
const year = new Date().getFullYear()
</script>

<template>
  <div class="legal">
    <header class="legal__top">
      <div class="container legal__top-inner">
        <RouterLink to="/" class="legal__wordmark">
          <span>Plug</span><span class="legal__cut">cut</span>
        </RouterLink>
        <LangSwitch />
      </div>
    </header>

    <main class="container legal__main">
      <RouterLink to="/" class="legal__back">← {{ t('legal.back') }}</RouterLink>
      <slot />
    </main>

    <footer class="legal__footer">
      <div class="container">© {{ year }} Plugcut. {{ t('footer.rights') }}</div>
    </footer>
  </div>
</template>

<style scoped>
.legal {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.legal__top {
  border-bottom: 1px solid var(--line-on-ink);
}
.legal__top-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
}
.legal__wordmark {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.4rem;
  letter-spacing: -0.03em;
}
.legal__cut {
  color: var(--accent);
}
.legal__main {
  flex: 1;
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
  max-width: 760px;
}
.legal__back {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.legal__back:hover {
  color: var(--accent);
}
.legal__footer {
  border-top: 1px solid var(--line-on-ink);
  padding-block: 1.5rem;
  font-family: var(--font-mono);
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
</style>
