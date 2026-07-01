<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { trustTier, type Reputation } from './types'

const props = defineProps<{ reputation: Reputation }>()
const { t } = useI18n()

const tier = computed(() => trustTier(props.reputation))
</script>

<template>
  <section class="rep" :class="`rep--${tier}`" :aria-label="t('reputation.title')">
    <header class="rep__head">
      <span class="rep__eyebrow">{{ t('reputation.title') }}</span>
      <span class="rep__tier">{{ t(`reputation.tier.${tier}`) }}</span>
    </header>

    <div v-if="reputation.has_track_record" class="rep__body">
      <div class="rep__score">
        <strong>{{ reputation.trust_score }}</strong>
        <span class="rep__score-max">/ 100</span>
      </div>
      <dl class="rep__stats">
        <div class="rep__stat">
          <dt>{{ t('reputation.sealed') }}</dt>
          <dd>{{ reputation.sealed_deals }}</dd>
        </div>
        <div class="rep__stat">
          <dt>{{ t('reputation.completed') }}</dt>
          <dd>{{ reputation.completed_deals }}</dd>
        </div>
        <div class="rep__stat">
          <dt>{{ t('reputation.asReferrer') }}</dt>
          <dd>{{ reputation.as_referrer }}</dd>
        </div>
        <div class="rep__stat">
          <dt>{{ t('reputation.asPlaced') }}</dt>
          <dd>{{ reputation.as_placed }}</dd>
        </div>
        <div v-if="reputation.disputed_deals > 0" class="rep__stat rep__stat--warn">
          <dt>{{ t('reputation.disputed') }}</dt>
          <dd>{{ reputation.disputed_deals }}</dd>
        </div>
      </dl>
    </div>

    <p v-else class="rep__empty">{{ t('reputation.empty') }}</p>
  </section>
</template>

<style scoped>
.rep {
  display: grid;
  gap: 1.1rem;
  padding: 1.4rem 1.5rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
}
.rep__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
}
.rep__eyebrow {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted-on-ink);
}
.rep__tier {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.24rem 0.6rem;
  border-radius: var(--radius-pill);
  background: var(--ink-3);
  color: var(--muted-on-ink);
}
.rep--trusted .rep__tier {
  background: var(--accent);
  color: var(--accent-ink);
}
.rep--established .rep__tier {
  background: var(--solid);
  color: var(--text-on-solid);
}
.rep__body {
  display: grid;
  gap: 1.2rem;
}
.rep__score {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}
.rep__score strong {
  font-family: var(--font-display);
  font-size: clamp(2.4rem, 6vw, 3.2rem);
  line-height: 1;
}
.rep__score-max {
  font-family: var(--font-mono);
  color: var(--muted-on-ink);
}
.rep__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.8rem;
}
.rep__stat {
  display: grid;
  gap: 0.15rem;
}
.rep__stat dt {
  font-family: var(--font-mono);
  font-size: 0.66rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted-on-ink);
}
.rep__stat dd {
  font-weight: 700;
  font-size: 1.2rem;
}
.rep__stat--warn dd {
  color: var(--danger);
}
.rep__empty {
  color: var(--muted-on-ink);
  font-size: var(--fs-small);
}
</style>
