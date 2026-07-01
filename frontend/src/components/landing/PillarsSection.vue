<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { UiCard, UiEyebrow } from '@/ui'

interface Pillar {
  title: string
  desc: string
}

const { tm } = useI18n()
const pillars = computed(() => tm('pillars.items') as Pillar[])
const glyphs = ['§', '✶', '↻', '◐']
</script>

<template>
  <section id="security" class="section pillars">
    <div class="container">
      <header class="pillars__head">
        <UiEyebrow tone="solid" class="pillars__eyebrow">{{ $t('pillars.eyebrow') }}</UiEyebrow>
        <h2 class="pillars__title">{{ $t('pillars.title') }}</h2>
      </header>

      <div class="pillars__grid">
        <UiCard v-for="(pillar, i) in pillars" :key="pillar.title" tone="solid" hover class="pillar">
          <span class="pillar__glyph" aria-hidden="true">{{ glyphs[i] }}</span>
          <h3 class="pillar__title">{{ pillar.title }}</h3>
          <p class="pillar__desc">{{ pillar.desc }}</p>
        </UiCard>
      </div>
    </div>
  </section>
</template>

<style scoped>
.pillars {
  background: var(--solid);
  color: var(--text-on-solid);
}
.pillars__head {
  max-width: 36rem;
  margin-bottom: 3.2rem;
}
.pillars__eyebrow {
  margin-bottom: 1rem;
}
.pillars__title {
  font-size: clamp(1.9rem, 4.5vw, 3rem);
}
.pillars__grid {
  display: grid;
  gap: 1.4rem;
  grid-template-columns: 1fr;
}
.pillar__glyph {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  /* Inverted on the dark card: a light chip with a near-black glyph. */
  background: var(--text-on-solid);
  color: var(--solid);
  font-size: 1.3rem;
  margin-bottom: 1.3rem;
}
.pillar__title {
  font-size: 1.3rem;
  margin-bottom: 0.6rem;
}
.pillar__desc {
  color: color-mix(in srgb, var(--text-on-solid) 64%, transparent);
  font-size: 0.96rem;
}
@media (min-width: 640px) {
  .pillars__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (min-width: 1024px) {
  .pillars__grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
