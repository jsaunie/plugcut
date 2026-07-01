<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import AppShell from '@/features/app/AppShell.vue'
import { searchProfiles } from '@/features/profiles/api'
import type { PublicProfile } from '@/features/profiles/types'
import { trustTier } from '@/features/reputation/types'
import { UiEyebrow, UiTextInput } from '@/ui'

const { t } = useI18n()

const skill = ref('')
const availableOnly = ref(true)
const results = ref<PublicProfile[]>([])
const loading = ref(true)

let timer: ReturnType<typeof setTimeout> | undefined

async function load(): Promise<void> {
  loading.value = true
  try {
    results.value = await searchProfiles(skill.value, availableOnly.value)
  } finally {
    loading.value = false
  }
}

// Debounce the skill input so typing does not fire a request per keystroke.
watch([skill, availableOnly], () => {
  clearTimeout(timer)
  timer = setTimeout(load, 250)
})

onMounted(load)
</script>

<template>
  <AppShell>
    <div class="head">
      <UiEyebrow>{{ t('directory.eyebrow') }}</UiEyebrow>
      <h1 class="head__title">{{ t('directory.title') }}</h1>
      <p class="head__lead">{{ t('directory.lead') }}</p>
    </div>

    <div class="filters">
      <UiTextInput v-model="skill" :placeholder="t('directory.skillPlaceholder')" />
      <label class="check">
        <input v-model="availableOnly" type="checkbox" />
        <span>{{ t('directory.availableOnly') }}</span>
      </label>
    </div>

    <p v-if="loading" class="muted">{{ t('common.loading') }}</p>

    <p v-else-if="!results.length" class="empty">{{ t('directory.empty') }}</p>

    <ul v-else class="list">
      <li v-for="row in results" :key="row.profile.id">
        <RouterLink :to="`/p/${row.profile.handle}`" class="card">
          <div class="card__main">
            <span class="card__name">{{ row.profile.display_name }}</span>
            <span v-if="row.profile.headline" class="card__headline">
              {{ row.profile.headline }}
            </span>
            <ul v-if="row.profile.skills.length" class="skills">
              <li v-for="s in row.profile.skills.slice(0, 6)" :key="s" class="skills__item">
                {{ s }}
              </li>
            </ul>
          </div>
          <div class="card__trust" :class="`card__trust--${trustTier(row.reputation)}`">
            <strong class="card__score">{{ row.reputation.trust_score }}</strong>
            <span class="card__tier">{{ t(`reputation.tier.${trustTier(row.reputation)}`) }}</span>
            <span class="card__deals">
              {{ t('directory.sealedCount', row.reputation.sealed_deals) }}
            </span>
          </div>
        </RouterLink>
      </li>
    </ul>
  </AppShell>
</template>

<style scoped>
.head {
  margin-bottom: 1.8rem;
}
.head__title {
  margin-top: 0.7rem;
  font-size: var(--fs-display-lg);
}
.head__lead {
  margin-top: 0.6rem;
  max-width: 54ch;
  color: var(--muted-on-ink);
}
.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.6rem;
}
.filters > :first-child {
  flex: 1 1 240px;
}
.check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--fs-small);
}
.muted,
.empty {
  color: var(--muted-on-ink);
}
.empty {
  padding: clamp(2rem, 5vw, 3rem);
  border: 1px dashed var(--line-on-ink);
  border-radius: var(--radius);
}
.list {
  list-style: none;
  display: grid;
  gap: 0.9rem;
}
.card {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
  align-items: center;
  justify-content: space-between;
  padding: 1.3rem 1.5rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
  transition:
    border-color var(--dur) ease,
    transform var(--dur) ease;
}
.card:hover {
  border-color: var(--text-on-ink);
  transform: translateY(-2px);
}
.card__main {
  display: grid;
  gap: 0.4rem;
  min-width: 0;
}
.card__name {
  font-weight: 700;
  font-size: 1.1rem;
}
.card__headline {
  color: var(--muted-on-ink);
  font-size: var(--fs-small);
}
.skills {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.15rem;
}
.skills__item {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  padding: 0.2rem 0.55rem;
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-pill);
}
.card__trust {
  display: grid;
  justify-items: end;
  gap: 0.1rem;
  text-align: right;
}
.card__score {
  font-family: var(--font-display);
  font-size: 1.8rem;
  line-height: 1;
}
.card__tier {
  font-family: var(--font-mono);
  font-size: 0.64rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted-on-ink);
}
.card__trust--trusted .card__tier {
  color: var(--accent-on-ink);
}
.card__deals {
  font-size: 0.72rem;
  color: var(--muted-on-ink);
}
</style>
