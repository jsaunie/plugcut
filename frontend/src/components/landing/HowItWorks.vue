<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { UiEyebrow } from '@/ui'

interface Step {
  n: string
  title: string
  desc: string
}

const { tm } = useI18n()
const steps = computed(() => tm('how.steps') as Step[])
</script>

<template>
  <section id="how" class="section">
    <div class="container">
      <header class="how__head">
        <UiEyebrow tone="accent" class="how__eyebrow">{{ $t('how.eyebrow') }}</UiEyebrow>
        <h2 class="how__title">{{ $t('how.title') }}</h2>
      </header>

      <ol class="how__steps">
        <li v-for="step in steps" :key="step.n" class="step">
          <span class="step__n">{{ step.n }}</span>
          <h3 class="step__title">{{ step.title }}</h3>
          <p class="step__desc">{{ step.desc }}</p>
        </li>
      </ol>
    </div>
  </section>
</template>

<style scoped>
.how__head {
  max-width: 32rem;
  margin-bottom: 3.5rem;
}
.how__eyebrow {
  margin-bottom: 1rem;
}
.how__title {
  font-size: clamp(1.9rem, 4.5vw, 3rem);
}
.how__steps {
  list-style: none;
  display: grid;
  gap: 1px;
  background: var(--line-on-ink);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
  overflow: hidden;
}
.step {
  background: var(--ink);
  padding: 2rem 1.8rem 2.2rem;
  transition: background 0.25s ease;
}
.step:hover {
  background: var(--ink-2);
}
.step__n {
  font-family: var(--font-mono);
  font-size: 0.95rem;
  color: var(--accent);
}
.step__title {
  font-size: 1.25rem;
  margin: 1.1rem 0 0.6rem;
}
.step__desc {
  color: var(--muted-on-ink);
  font-size: 0.95rem;
}
@media (min-width: 720px) {
  .how__steps {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (min-width: 1080px) {
  .how__steps {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
