<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import LangSwitch from '@/components/shared/LangSwitch.vue'
import { UiButton } from '@/ui'

const scrolled = ref(false)
const onScroll = () => (scrolled.value = window.scrollY > 12)

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <header class="hdr" :class="{ 'hdr--scrolled': scrolled }">
    <div class="container hdr__inner">
      <RouterLink to="/" class="wordmark" aria-label="Plugcut">
        <span>Plug</span><span class="wordmark__cut">cut</span>
        <span class="wordmark__dot" aria-hidden="true">✂</span>
      </RouterLink>

      <nav class="hdr__nav">
        <a href="#how">{{ $t('nav.how') }}</a>
        <a href="#security">{{ $t('nav.security') }}</a>
        <a href="#calculateur">{{ $t('nav.calculator') }}</a>
        <a href="#faq">{{ $t('nav.faq') }}</a>
      </nav>

      <div class="hdr__actions">
        <LangSwitch />
        <RouterLink to="/connexion" class="hdr__login">{{ $t('nav.login') }}</RouterLink>
        <UiButton to="/inscription" class="hdr__start">{{ $t('nav.start') }}</UiButton>
      </div>
    </div>
  </header>
</template>

<style scoped>
.hdr {
  position: fixed;
  inset: 0 0 auto 0;
  z-index: 50;
  transition:
    background 0.3s ease,
    border-color 0.3s ease,
    backdrop-filter 0.3s ease;
  border-bottom: 1px solid transparent;
}
.hdr--scrolled {
  background: rgba(11, 11, 13, 0.72);
  backdrop-filter: blur(14px) saturate(140%);
  border-bottom-color: var(--line-on-ink);
}
.hdr__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  height: 72px;
}
.wordmark {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.4rem;
  letter-spacing: -0.03em;
  display: inline-flex;
  align-items: center;
}
.wordmark__cut {
  color: var(--accent);
}
.wordmark__dot {
  font-size: 0.7rem;
  margin-left: 0.3rem;
  transform: translateY(-0.5em) rotate(8deg);
  opacity: 0.85;
}
.hdr__nav {
  display: none;
  gap: 1.8rem;
  font-size: 0.92rem;
  color: var(--muted-on-ink);
}
.hdr__nav a {
  position: relative;
  transition: color 0.15s ease;
}
.hdr__nav a:hover {
  color: var(--text-on-ink);
}
.hdr__nav a::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -6px;
  width: 0;
  height: 2px;
  background: var(--accent);
  transition: width 0.2s ease;
}
.hdr__nav a:hover::after {
  width: 100%;
}
.hdr__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.hdr__login {
  display: none;
  font-size: 0.92rem;
  color: var(--muted-on-ink);
}
.hdr__login:hover {
  color: var(--text-on-ink);
}
.hdr__start {
  padding: 0.55rem 1.05rem;
  font-size: 0.9rem;
}
@media (min-width: 900px) {
  .hdr__nav {
    display: flex;
  }
  .hdr__login {
    display: inline;
  }
}
</style>
