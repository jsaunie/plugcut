<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="section ctaband">
    <div class="container">
      <div class="ctaband__box">
        <div class="ctaband__noise" aria-hidden="true" />
        <h2 class="ctaband__title">{{ $t('cta.title') }}</h2>
        <p class="ctaband__subtitle">{{ $t('cta.subtitle') }}</p>
        <RouterLink to="/inscription" class="btn btn--dark ctaband__btn">
          {{ $t('cta.button') }} <span aria-hidden="true">→</span>
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.ctaband__box {
  position: relative;
  overflow: hidden;
  text-align: center;
  padding: clamp(3rem, 8vw, 6rem) clamp(1.5rem, 5vw, 4rem);
  background: var(--accent);
  color: var(--accent-ink);
  border-radius: calc(var(--radius) + 8px);
}
.ctaband__noise {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(11, 11, 13, 0.16) 1px, transparent 1px);
  background-size: 7px 7px;
  opacity: 0.5;
  pointer-events: none;
}
.ctaband__title {
  position: relative;
  font-size: clamp(2rem, 6vw, 3.6rem);
  max-width: 18ch;
  margin-inline: auto;
}
.ctaband__subtitle {
  position: relative;
  margin: 1.2rem auto 2rem;
  max-width: 44ch;
  font-weight: 500;
  opacity: 0.78;
}
.ctaband__btn {
  position: relative;
}
</style>
