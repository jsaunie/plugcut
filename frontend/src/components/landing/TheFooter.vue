<script setup lang="ts">
import { RouterLink } from 'vue-router'

import LangSwitch from '@/components/shared/LangSwitch.vue'

const year = new Date().getFullYear()
</script>

<template>
  <footer class="footer">
    <div class="container footer__inner">
      <div class="footer__brand">
        <RouterLink to="/" class="footer__wordmark">
          <span>Plug</span><span class="footer__cut">cut</span>
        </RouterLink>
        <p class="footer__tagline">{{ $t('footer.tagline') }}</p>
        <LangSwitch />
      </div>

      <nav class="footer__col">
        <span class="footer__col-title">{{ $t('footer.product') }}</span>
        <a href="#how">{{ $t('nav.how') }}</a>
        <a href="#security">{{ $t('nav.security') }}</a>
        <a href="#calculateur">{{ $t('nav.calculator') }}</a>
        <a href="#faq">{{ $t('nav.faq') }}</a>
      </nav>

      <nav class="footer__col">
        <span class="footer__col-title">{{ $t('footer.legal') }}</span>
        <RouterLink to="/mentions-legales">{{ $t('footer.legalNotice') }}</RouterLink>
        <RouterLink to="/cgu">{{ $t('footer.terms') }}</RouterLink>
        <RouterLink to="/confidentialite">{{ $t('footer.privacy') }}</RouterLink>
      </nav>
    </div>

    <div class="container footer__bottom">
      <span>© {{ year }} Plugcut. {{ $t('footer.rights') }}</span>
      <span class="footer__disclaimer">{{ $t('footer.disclaimer') }}</span>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  border-top: 1px solid var(--line-on-ink);
  padding-top: 4rem;
  padding-bottom: 2rem;
}
.footer__inner {
  display: grid;
  gap: 2.5rem;
  grid-template-columns: 1fr;
}
.footer__wordmark {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.5rem;
  letter-spacing: -0.03em;
}
.footer__cut {
  color: var(--accent);
}
.footer__tagline {
  margin: 0.9rem 0 1.3rem;
  max-width: 30ch;
  color: var(--muted-on-ink);
  font-size: 0.95rem;
}
.footer__col {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  font-size: 0.95rem;
  color: var(--muted-on-ink);
}
.footer__col-title {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-on-ink);
  margin-bottom: 0.3rem;
}
.footer__col a:hover {
  color: var(--accent);
}
.footer__bottom {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 3.5rem;
  padding-top: 1.6rem;
  border-top: 1px solid var(--line-on-ink);
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: var(--muted-on-ink);
}
@media (min-width: 760px) {
  .footer__inner {
    grid-template-columns: 2fr 1fr 1fr;
  }
}
</style>
