<script setup lang="ts">
import { RouterLink } from 'vue-router'

import LangSwitch from '@/components/shared/LangSwitch.vue'

defineProps<{ title: string; subtitle: string }>()
</script>

<template>
  <div class="auth">
    <div class="auth__glow" aria-hidden="true" />
    <div class="auth__top container">
      <RouterLink to="/" class="auth__wordmark">
        <span>Plug</span><span class="auth__cut">cut</span>
      </RouterLink>
      <LangSwitch />
    </div>

    <main class="auth__main">
      <div class="auth__card">
        <h1 class="auth__title">{{ title }}</h1>
        <p class="auth__subtitle">{{ subtitle }}</p>
        <slot />
      </div>
    </main>
  </div>
</template>

<style scoped>
.auth {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.auth__glow {
  position: absolute;
  top: -20%;
  left: 50%;
  transform: translateX(-50%);
  width: 70vw;
  max-width: 700px;
  aspect-ratio: 1;
  background: radial-gradient(circle, rgba(216, 255, 54, 0.12), transparent 62%);
  filter: blur(30px);
  pointer-events: none;
}
.auth__top {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1.5rem;
}
.auth__wordmark {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.4rem;
  letter-spacing: -0.03em;
}
.auth__cut {
  color: var(--accent);
}
.auth__main {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem var(--gutter) 4rem;
}
.auth__card {
  width: 100%;
  max-width: 420px;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
  padding: clamp(1.8rem, 4vw, 2.6rem);
}
.auth__title {
  font-size: var(--fs-display-md);
}
.auth__subtitle {
  margin: 0.7rem 0 1.8rem;
  color: var(--muted-on-ink);
}
</style>
