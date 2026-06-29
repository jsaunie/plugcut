<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface QA {
  q: string
  a: string
}

const { tm } = useI18n()
const items = computed(() => tm('faq.items') as QA[])
</script>

<template>
  <section id="faq" class="section faq">
    <div class="container faq__inner">
      <header class="faq__head">
        <p class="eyebrow faq__eyebrow">{{ $t('faq.eyebrow') }}</p>
        <h2 class="faq__title">{{ $t('faq.title') }}</h2>
      </header>

      <div class="faq__list">
        <details v-for="(item, i) in items" :key="i" class="qa" :open="i === 0">
          <summary class="qa__q">
            <span>{{ item.q }}</span>
            <span class="qa__sign" aria-hidden="true" />
          </summary>
          <p class="qa__a">{{ item.a }}</p>
        </details>
      </div>
    </div>
  </section>
</template>

<style scoped>
.faq__inner {
  display: grid;
  gap: 2.5rem;
}
.faq__eyebrow {
  color: var(--accent-deep);
  margin-bottom: 1rem;
}
.faq__title {
  font-size: clamp(1.9rem, 4.5vw, 3rem);
}
.qa {
  border-bottom: 1px solid var(--line-on-ink);
}
.qa__q {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.5rem 0;
  font-family: var(--font-display);
  font-size: clamp(1.1rem, 2.5vw, 1.4rem);
  font-weight: 600;
  list-style: none;
  cursor: pointer;
}
.qa__q::-webkit-details-marker {
  display: none;
}
.qa__sign {
  position: relative;
  flex: none;
  width: 18px;
  height: 18px;
}
.qa__sign::before,
.qa__sign::after {
  content: '';
  position: absolute;
  background: var(--accent);
  transition: transform 0.25s ease;
}
.qa__sign::before {
  top: 8px;
  left: 0;
  width: 18px;
  height: 2px;
}
.qa__sign::after {
  top: 0;
  left: 8px;
  width: 2px;
  height: 18px;
}
.qa[open] .qa__sign::after {
  transform: scaleY(0);
}
.qa__a {
  padding-bottom: 1.6rem;
  max-width: 64ch;
  color: var(--muted-on-ink);
  font-size: 1rem;
}
@media (min-width: 900px) {
  .faq__inner {
    grid-template-columns: 0.8fr 1.2fr;
  }
}
</style>
