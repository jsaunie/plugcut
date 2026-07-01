<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'

import LangSwitch from '@/components/shared/LangSwitch.vue'
import { getPublicProfile } from '@/features/profiles/api'
import type { PublicProfile } from '@/features/profiles/types'
import ReputationCard from '@/features/reputation/ReputationCard.vue'
import { UiButton, UiEyebrow } from '@/ui'

const { t } = useI18n()
const route = useRoute()
const handle = route.params.handle as string

const data = ref<PublicProfile | null>(null)
const loading = ref(true)
const notFound = ref(false)

onMounted(async () => {
  try {
    data.value = await getPublicProfile(handle)
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="pp">
    <header class="pp__top">
      <div class="container pp__top-inner">
        <RouterLink to="/" class="pp__wordmark">
          <span>Plug</span><span class="pp__cut">cut</span>
        </RouterLink>
        <LangSwitch />
      </div>
    </header>

    <main class="container pp__main">
      <p v-if="loading" class="muted">{{ t('common.loading') }}</p>

      <div v-else-if="notFound" class="card">
        <h1 class="card__title">{{ t('publicProfile.notFoundTitle') }}</h1>
        <p class="muted">{{ t('publicProfile.notFoundLead') }}</p>
        <UiButton to="/" variant="ghost">{{ t('publicProfile.backHome') }}</UiButton>
      </div>

      <div v-else-if="data" class="layout">
        <section class="card ident">
          <UiEyebrow>{{ t('publicProfile.eyebrow') }}</UiEyebrow>
          <h1 class="ident__name">{{ data.profile.display_name }}</h1>
          <p v-if="data.profile.headline" class="ident__headline">
            {{ data.profile.headline }}
          </p>
          <span
            class="ident__avail"
            :class="data.profile.available ? 'ident__avail--on' : 'ident__avail--off'"
          >
            {{
              data.profile.available
                ? t('publicProfile.available')
                : t('publicProfile.unavailable')
            }}
          </span>

          <ul v-if="data.profile.skills.length" class="skills">
            <li v-for="skill in data.profile.skills" :key="skill" class="skills__item">
              {{ skill }}
            </li>
          </ul>

          <p v-if="data.profile.bio" class="ident__bio">{{ data.profile.bio }}</p>
        </section>

        <aside class="side">
          <ReputationCard :reputation="data.reputation" />
          <p class="side__note">{{ t('publicProfile.repNote') }}</p>
        </aside>
      </div>
    </main>
  </div>
</template>

<style scoped>
.pp {
  min-height: 100vh;
  background: var(--ink);
}
.pp__top {
  border-bottom: 1px solid var(--line-on-ink);
}
.pp__top-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.1rem 0;
}
.pp__wordmark {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.25rem;
}
.pp__cut {
  color: var(--accent-on-ink);
}
.pp__main {
  padding: clamp(2rem, 6vw, 4rem) 0;
}
.muted {
  color: var(--muted-on-ink);
}
.layout {
  display: grid;
  gap: 1.4rem;
  align-items: start;
}
@media (min-width: 880px) {
  .layout {
    grid-template-columns: 1.4fr 1fr;
  }
}
.card {
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
  padding: clamp(1.4rem, 3.5vw, 2rem);
  display: grid;
  gap: 1rem;
  align-content: start;
}
.card__title {
  font-size: var(--fs-display-md);
}
.ident__name {
  font-size: var(--fs-display-md);
  line-height: var(--lh-heading);
}
.ident__headline {
  color: var(--muted-on-ink);
  font-size: var(--fs-body-lg);
}
.ident__avail {
  justify-self: start;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.24rem 0.6rem;
  border-radius: var(--radius-pill);
}
.ident__avail--on {
  background: var(--accent);
  color: var(--accent-ink);
}
.ident__avail--off {
  background: var(--ink-3);
  color: var(--muted-on-ink);
}
.skills {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.skills__item {
  font-family: var(--font-mono);
  font-size: var(--fs-small);
  padding: 0.3rem 0.7rem;
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-pill);
}
.ident__bio {
  color: var(--text-on-ink);
  line-height: var(--lh-body);
  white-space: pre-line;
}
.side {
  display: grid;
  gap: 0.8rem;
}
.side__note {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
</style>
