<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import AppShell from '@/features/app/AppShell.vue'
import { getIntros, respondIntro } from '@/features/intros/api'
import type { Intro } from '@/features/intros/types'
import { formatDate } from '@/shared/format'
import { UiButton, UiEyebrow } from '@/ui'

const { t, locale } = useI18n()

const inbound = ref<Intro[]>([])
const outbound = ref<Intro[]>([])
const loading = ref(true)
const busy = ref('')

function day(iso: string): string {
  return formatDate(iso, locale.value)
}

async function load(): Promise<void> {
  const inbox = await getIntros()
  inbound.value = inbox.inbound
  outbound.value = inbox.outbound
  loading.value = false
}

async function respond(intro: Intro, accept: boolean): Promise<void> {
  busy.value = intro.id
  try {
    await respondIntro(intro.id, accept)
    await load()
  } finally {
    busy.value = ''
  }
}

onMounted(load)
</script>

<template>
  <AppShell>
    <div class="head">
      <UiEyebrow>{{ t('intros.eyebrow') }}</UiEyebrow>
      <h1 class="head__title">{{ t('intros.title') }}</h1>
      <p class="head__lead">{{ t('intros.lead') }}</p>
    </div>

    <p v-if="loading" class="muted">{{ t('common.loading') }}</p>

    <template v-else>
      <section class="block">
        <h2 class="block__title">{{ t('intros.inboundTitle') }}</h2>
        <p v-if="!inbound.length" class="muted">{{ t('intros.inboundEmpty') }}</p>
        <ul v-else class="list">
          <li v-for="intro in inbound" :key="intro.id" class="card">
            <div class="card__main">
              <RouterLink
                v-if="intro.counterpart"
                :to="`/p/${intro.counterpart.handle}`"
                class="card__name"
              >
                {{ intro.counterpart.display_name }}
              </RouterLink>
              <span v-else class="card__name">{{ t('intros.unknown') }}</span>
              <p v-if="intro.message" class="card__msg">{{ intro.message }}</p>
              <span class="card__date">{{ day(intro.created_at) }}</span>
            </div>
            <div class="card__side">
              <div v-if="intro.status === 'pending'" class="card__actions">
                <UiButton :loading="busy === intro.id" @click="respond(intro, true)">
                  {{ t('intros.accept') }}
                </UiButton>
                <button
                  class="decline"
                  :disabled="busy === intro.id"
                  @click="respond(intro, false)"
                >
                  {{ t('intros.decline') }}
                </button>
              </div>
              <span v-else class="status" :class="`status--${intro.status}`">
                {{ t(`intros.status.${intro.status}`) }}
              </span>
            </div>
          </li>
        </ul>
      </section>

      <section class="block">
        <h2 class="block__title">{{ t('intros.outboundTitle') }}</h2>
        <p v-if="!outbound.length" class="muted">{{ t('intros.outboundEmpty') }}</p>
        <ul v-else class="list">
          <li v-for="intro in outbound" :key="intro.id" class="card">
            <div class="card__main">
              <RouterLink
                v-if="intro.counterpart"
                :to="`/p/${intro.counterpart.handle}`"
                class="card__name"
              >
                {{ intro.counterpart.display_name }}
              </RouterLink>
              <span v-else class="card__name">{{ t('intros.unknown') }}</span>
              <span class="card__date">{{ day(intro.created_at) }}</span>
            </div>
            <span class="status" :class="`status--${intro.status}`">
              {{ t(`intros.status.${intro.status}`) }}
            </span>
          </li>
        </ul>
      </section>
    </template>
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
.muted {
  color: var(--muted-on-ink);
}
.block {
  margin-bottom: 2.4rem;
}
.block__title {
  font-size: var(--fs-title);
  margin-bottom: 1rem;
}
.list {
  list-style: none;
  display: grid;
  gap: 0.9rem;
}
.card {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  padding: 1.2rem 1.4rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
}
.card__main {
  display: grid;
  gap: 0.3rem;
  min-width: 0;
}
.card__name {
  font-weight: 700;
}
.card__msg {
  color: var(--text-on-ink);
  font-size: var(--fs-small);
}
.card__date {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--muted-on-ink);
}
.card__actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.decline {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
  text-decoration: underline;
}
.status {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.24rem 0.6rem;
  border-radius: var(--radius-pill);
  background: var(--ink-3);
  color: var(--muted-on-ink);
}
.status--accepted {
  background: var(--accent);
  color: var(--accent-ink);
}
</style>
