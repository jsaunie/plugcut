<script setup lang="ts">
import { UiButton, UiEyebrow } from '@/ui'
</script>

<template>
  <section class="hero">
    <div class="hero__glow" aria-hidden="true" />
    <div class="container hero__inner">
      <div class="hero__copy">
        <UiEyebrow class="hero__badge rise" style="animation-delay: 0.05s">
          {{ $t('hero.badge') }}
        </UiEyebrow>

        <h1 class="hero__title">
          <span class="rise" style="animation-delay: 0.12s">{{ $t('hero.title1') }}</span>
          <span class="hero__title-cut rise" style="animation-delay: 0.22s">
            {{ $t('hero.title2') }}
          </span>
        </h1>

        <p class="hero__subtitle rise" style="animation-delay: 0.32s">
          {{ $t('hero.subtitle') }}
        </p>

        <div class="hero__actions rise" style="animation-delay: 0.42s">
          <UiButton to="/inscription" size="lg">
            {{ $t('hero.ctaPrimary') }} <span aria-hidden="true">→</span>
          </UiButton>
          <UiButton href="#how" variant="ghost" size="lg">
            {{ $t('hero.ctaSecondary') }}
          </UiButton>
        </div>

        <p class="hero__note rise" style="animation-delay: 0.52s">
          <span aria-hidden="true">🔒</span> {{ $t('hero.note') }}
        </p>
      </div>

      <!-- Signature visual: a referral "receipt" with a perforated cut line -->
      <div class="hero__receipt rise" style="animation-delay: 0.3s">
        <article class="receipt" aria-hidden="true">
          <header class="receipt__head">
            <span class="receipt__brand">PLUGCUT</span>
            <span class="receipt__label">{{ $t('hero.receipt.label') }}</span>
          </header>

          <dl class="receipt__rows">
            <div class="receipt__row">
              <dt>{{ $t('hero.receipt.client') }}</dt>
              <dd class="receipt__redacted">{{ $t('hero.receipt.clientValue') }}</dd>
            </div>
            <div class="receipt__row">
              <dt>{{ $t('hero.receipt.tjm') }}</dt>
              <dd>500 €</dd>
            </div>
            <div class="receipt__row">
              <dt>{{ $t('hero.receipt.rate') }}</dt>
              <dd>10 %</dd>
            </div>
            <div class="receipt__row">
              <dt>{{ $t('hero.receipt.duration') }}</dt>
              <dd>{{ $t('hero.receipt.months') }}</dd>
            </div>
          </dl>

          <div class="receipt__cut">
            <span class="receipt__scissors">✂</span>
          </div>

          <div class="receipt__total">
            <span>{{ $t('hero.receipt.yourCut') }}</span>
            <strong>1 000 €</strong>
          </div>

          <span class="receipt__stamp">{{ $t('hero.receipt.stamp') }}</span>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  padding-top: 150px;
  padding-bottom: var(--section-pad);
  overflow: hidden;
}
.hero__glow {
  position: absolute;
  top: -10%;
  right: -5%;
  width: 60vw;
  height: 60vw;
  max-width: 760px;
  max-height: 760px;
  background: radial-gradient(circle, rgba(216, 255, 54, 0.16), transparent 62%);
  filter: blur(30px);
  pointer-events: none;
}
.hero__inner {
  position: relative;
  display: grid;
  grid-template-columns: 1fr;
  gap: clamp(3rem, 6vw, 5rem);
  align-items: center;
}
.hero__badge {
  margin-bottom: 1.8rem;
}
.hero__title {
  font-size: clamp(3rem, 8vw, 5.6rem);
  display: flex;
  flex-direction: column;
}
.hero__title-cut {
  position: relative;
  width: fit-content;
  color: var(--accent);
}
.hero__title-cut::after {
  content: '';
  position: absolute;
  left: -2%;
  right: -2%;
  top: 52%;
  height: 3px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  animation: cut-strike 0.6s cubic-bezier(0.65, 0, 0.35, 1) 0.9s both;
  opacity: 0.55;
}
@keyframes cut-strike {
  to {
    transform: scaleX(1);
  }
}
.hero__subtitle {
  margin-top: 1.6rem;
  max-width: 36ch;
  font-size: 1.12rem;
  color: var(--muted-on-ink);
}
.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.9rem;
  margin-top: 2.2rem;
}
.hero__note {
  margin-top: 1.6rem;
  font-size: 0.86rem;
  color: var(--muted-on-ink);
}

/* ---- Receipt visual ---- */
.hero__receipt {
  display: flex;
  justify-content: center;
}
.receipt {
  position: relative;
  width: min(340px, 84vw);
  background: var(--paper);
  color: var(--text-on-paper);
  border-radius: 6px;
  padding: 1.6rem 1.5rem 1.4rem;
  font-family: var(--font-mono);
  box-shadow:
    0 40px 80px -30px rgba(0, 0, 0, 0.7),
    0 0 0 1px rgba(0, 0, 0, 0.05);
  transform: rotate(-2.4deg);
  transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}
.hero__receipt:hover .receipt {
  transform: rotate(0deg) translateY(-4px);
}
.receipt__head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--line-on-paper);
}
.receipt__brand {
  font-weight: 700;
  letter-spacing: 0.18em;
  font-size: 0.82rem;
}
.receipt__label {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted-on-paper);
}
.receipt__rows {
  padding: 1rem 0;
  display: grid;
  gap: 0.7rem;
}
.receipt__row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}
.receipt__row dt {
  color: var(--muted-on-paper);
}
.receipt__row dd {
  font-weight: 700;
}
.receipt__redacted {
  background: var(--text-on-paper);
  color: var(--text-on-paper);
  border-radius: 3px;
  padding-inline: 0.5rem;
  user-select: none;
}
.receipt__cut {
  position: relative;
  height: 18px;
  margin: 0.4rem -1.5rem;
  border-top: 2px dashed var(--line-on-paper);
}
/* ticket notches on each side of the perforation */
.receipt__cut::before,
.receipt__cut::after {
  content: '';
  position: absolute;
  top: -11px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--ink);
}
.receipt__cut::before {
  left: -10px;
}
.receipt__cut::after {
  right: -10px;
}
.receipt__scissors {
  position: absolute;
  top: 50%;
  left: 1.5rem;
  transform: translateY(-50%);
  background: var(--paper);
  padding-inline: 0.35rem;
  font-size: 0.85rem;
}
.receipt__total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.8rem;
  padding: 0.7rem 0.85rem;
  background: var(--accent);
  border-radius: 6px;
}
.receipt__total span {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.receipt__total strong {
  font-size: 1.35rem;
}
.receipt__stamp {
  position: absolute;
  right: -10px;
  bottom: 64px;
  font-family: var(--font-body);
  font-weight: 700;
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent-deep);
  border: 2px solid var(--accent-deep);
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  transform: rotate(-12deg);
  opacity: 0.85;
}

@media (min-width: 980px) {
  .hero__inner {
    grid-template-columns: 1.1fr 0.9fr;
  }
}
</style>
