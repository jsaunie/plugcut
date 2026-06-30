<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import LegalLayout from '@/features/legal/LegalLayout.vue'

interface Section {
  heading: string
  body: string
}

const props = defineProps<{ doc: 'notice' | 'terms' | 'privacy' }>()

const { t, tm } = useI18n()
const sections = computed(() => tm(`legal.${props.doc}.sections`) as Section[])
</script>

<template>
  <LegalLayout>
    <article class="doc">
      <h1 class="doc__title">{{ t(`legal.${doc}.title`) }}</h1>
      <p class="doc__updated">{{ t('legal.updated') }} : {{ t('legal.updatedValue') }}</p>

      <section v-for="(section, index) in sections" :key="index" class="doc__section">
        <h2 class="doc__heading">{{ section.heading }}</h2>
        <p class="doc__body">{{ section.body }}</p>
      </section>

      <p class="doc__demo">{{ t('legal.demoNote') }}</p>
    </article>
  </LegalLayout>
</template>

<style scoped>
.doc__title {
  margin-top: 1.2rem;
  font-size: var(--fs-display-md);
}
.doc__updated {
  margin-top: 0.6rem;
  font-family: var(--font-mono);
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.doc__section {
  margin-top: 2rem;
}
.doc__heading {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}
.doc__body {
  color: var(--muted-on-ink);
}
.doc__demo {
  margin-top: 2.5rem;
  padding: 1rem 1.2rem;
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-sm);
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
</style>
