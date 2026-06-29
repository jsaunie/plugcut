<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

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
        <p class="eyebrow pillars__eyebrow">{{ $t('pillars.eyebrow') }}</p>
        <h2 class="pillars__title">{{ $t('pillars.title') }}</h2>
      </header>

      <div class="pillars__grid">
        <article v-for="(pillar, i) in pillars" :key="pillar.title" class="pillar">
          <span class="pillar__glyph" aria-hidden="true">{{ glyphs[i] }}</span>
          <h3 class="pillar__title">{{ pillar.title }}</h3>
          <p class="pillar__desc">{{ pillar.desc }}</p>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.pillars {
  background: var(--paper);
  color: var(--text-on-paper);
}
.pillars__head {
  max-width: 24ch;
  margin-bottom: 3.2rem;
}
.pillars__eyebrow {
  color: var(--text-on-paper);
  opacity: 0.7;
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
.pillar {
  padding: 1.9rem 1.7rem 2rem;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid var(--line-on-paper);
  border-radius: var(--radius);
  transition:
    transform 0.25s ease,
    border-color 0.25s ease;
}
.pillar:hover {
  transform: translateY(-4px);
  border-color: var(--text-on-paper);
}
.pillar__glyph {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--accent);
  color: var(--accent-ink);
  font-size: 1.3rem;
  margin-bottom: 1.3rem;
}
.pillar__title {
  font-size: 1.3rem;
  margin-bottom: 0.6rem;
}
.pillar__desc {
  color: var(--muted-on-paper);
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
