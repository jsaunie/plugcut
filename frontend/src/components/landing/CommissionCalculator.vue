<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { UiEyebrow } from '@/ui'

const { locale } = useI18n()

// Same shape as the backend domain: monthly cut = TJM x days x rate, total = monthly x months.
const tjm = ref(550)
const rate = ref(10)
const months = ref(12)
const daysPerMonth = ref(20)

const monthly = computed(() => tjm.value * daysPerMonth.value * (rate.value / 100))
const total = computed(() => monthly.value * months.value)

const currency = computed(() =>
  new Intl.NumberFormat(locale.value === 'en' ? 'en-IE' : 'fr-FR', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }),
)
const fmt = (value: number) => currency.value.format(value)
</script>

<template>
  <section id="calculateur" class="section calc">
    <div class="container calc__inner">
      <header class="calc__head">
        <UiEyebrow tone="accent" class="calc__eyebrow">{{ $t('calc.eyebrow') }}</UiEyebrow>
        <h2 class="calc__title">{{ $t('calc.title') }}</h2>
        <p class="calc__subtitle">{{ $t('calc.subtitle') }}</p>
      </header>

      <div class="calc__panel">
        <div class="calc__controls">
          <label class="field">
            <span class="field__label">{{ $t('calc.tjm') }}</span>
            <span class="field__value">{{ fmt(tjm) }}</span>
            <input v-model.number="tjm" type="range" min="200" max="1500" step="10" />
          </label>

          <label class="field">
            <span class="field__label">{{ $t('calc.rate') }}</span>
            <span class="field__value">{{ rate }} %</span>
            <input v-model.number="rate" type="range" min="1" max="30" step="1" />
          </label>

          <label class="field">
            <span class="field__label">{{ $t('calc.duration') }}</span>
            <span class="field__value">{{ months }} {{ $t('calc.durationUnit') }}</span>
            <input v-model.number="months" type="range" min="1" max="36" step="1" />
          </label>

          <label class="field">
            <span class="field__label">{{ $t('calc.daysPerMonth') }}</span>
            <span class="field__value">{{ daysPerMonth }}</span>
            <input v-model.number="daysPerMonth" type="range" min="1" max="23" step="1" />
          </label>
        </div>

        <aside class="calc__result">
          <div class="calc__result-block">
            <span class="calc__result-label">{{ $t('calc.monthly') }}</span>
            <strong class="calc__result-monthly">{{ fmt(monthly) }}</strong>
          </div>
          <div class="perforation calc__result-cut">
            <span class="perforation__scissors" aria-hidden="true">✂</span>
          </div>
          <div class="calc__result-block">
            <span class="calc__result-label">{{ $t('calc.total') }}</span>
            <strong class="calc__result-total">{{ fmt(total) }}</strong>
          </div>
          <p class="calc__disclaimer">{{ $t('calc.disclaimer') }}</p>
        </aside>
      </div>
    </div>
  </section>
</template>

<style scoped>
.calc__inner {
  display: grid;
  gap: 3rem;
}
.calc__head {
  max-width: 34rem;
}
.calc__eyebrow {
  margin-bottom: 1rem;
}
.calc__title {
  font-size: clamp(1.9rem, 4.5vw, 3rem);
}
.calc__subtitle {
  margin-top: 1rem;
  color: var(--muted-on-ink);
  max-width: 46ch;
}
.calc__panel {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: 1fr;
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
  padding: clamp(1.5rem, 3vw, 2.4rem);
  background: linear-gradient(160deg, var(--ink-2), var(--ink));
}
.calc__controls {
  display: grid;
  gap: 1.7rem;
  align-content: start;
}
.field {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: baseline;
  gap: 0.4rem 1rem;
}
.field__label {
  font-size: 0.9rem;
  color: var(--muted-on-ink);
}
.field__value {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--accent);
  text-align: right;
}
.field input[type='range'] {
  grid-column: 1 / -1;
  width: 100%;
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  border-radius: 999px;
  background: var(--ink-3);
  outline: none;
  margin-top: 0.4rem;
}
.field input[type='range']::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--accent);
  cursor: grab;
  border: 3px solid var(--ink);
  box-shadow: 0 0 0 1px var(--accent);
}
.field input[type='range']::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--accent);
  cursor: grab;
  border: 3px solid var(--ink);
}
.calc__result {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1.1rem;
  padding: 1.8rem;
  background: var(--accent);
  color: var(--accent-ink);
  border-radius: calc(var(--radius) - 4px);
}
.calc__result-label {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.75;
}
.calc__result-monthly {
  display: block;
  font-family: var(--font-display);
  font-size: clamp(2rem, 5vw, 2.6rem);
  line-height: 1;
  margin-top: 0.3rem;
}
.calc__result-total {
  display: block;
  font-family: var(--font-display);
  font-size: clamp(2.6rem, 6vw, 3.6rem);
  line-height: 1;
  margin-top: 0.3rem;
}
.calc__result-cut {
  border-color: rgba(11, 11, 13, 0.3);
}
.calc__result-cut .perforation__scissors {
  background: var(--accent);
  color: var(--accent-ink);
  left: 0;
}
.calc__disclaimer {
  font-size: 0.74rem;
  line-height: 1.45;
  opacity: 0.72;
}
@media (min-width: 860px) {
  .calc__panel {
    grid-template-columns: 1.15fr 0.85fr;
    gap: 2.5rem;
  }
}
</style>
