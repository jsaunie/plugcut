<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import AppShell from '@/features/app/AppShell.vue'
import { getMyProfile, upsertMyProfile } from '@/features/profiles/api'
import { getMyReputation } from '@/features/reputation/api'
import ReputationCard from '@/features/reputation/ReputationCard.vue'
import type { Reputation } from '@/features/reputation/types'
import { ApiError } from '@/shared/http'
import { UiButton, UiEyebrow, UiField, UiTextarea, UiTextInput } from '@/ui'

const { t } = useI18n()

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const saved = ref(false)

const handle = ref('')
const displayName = ref('')
const headline = ref('')
const skills = ref('')
const bio = ref('')
const available = ref(true)

const reputation = ref<Reputation | null>(null)

const publicUrl = computed(() =>
  handle.value ? `${window.location.origin}/p/${handle.value}` : '',
)

onMounted(async () => {
  try {
    const profile = await getMyProfile()
    handle.value = profile.handle
    displayName.value = profile.display_name
    headline.value = profile.headline
    skills.value = profile.skills.join(', ')
    bio.value = profile.bio
    available.value = profile.available
  } catch (err) {
    // 404 just means the profile does not exist yet: keep the empty form.
    if (err instanceof ApiError && err.status !== 404) {
      error.value = err.message
    }
  }
  try {
    reputation.value = await getMyReputation()
  } catch {
    reputation.value = null
  }
  loading.value = false
})

async function save(): Promise<void> {
  error.value = ''
  saved.value = false
  saving.value = true
  try {
    const profile = await upsertMyProfile({
      handle: handle.value.trim(),
      display_name: displayName.value.trim(),
      headline: headline.value.trim(),
      bio: bio.value.trim(),
      available: available.value,
      skills: skills.value
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
    })
    handle.value = profile.handle
    saved.value = true
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : t('profile.errors.generic')
  } finally {
    saving.value = false
  }
}

async function copyPublicUrl(): Promise<void> {
  await navigator.clipboard.writeText(publicUrl.value)
  saved.value = false
}
</script>

<template>
  <AppShell>
    <div class="head">
      <UiEyebrow>{{ t('profile.eyebrow') }}</UiEyebrow>
      <h1 class="head__title">{{ t('profile.title') }}</h1>
      <p class="head__lead">{{ t('profile.lead') }}</p>
    </div>

    <p v-if="loading" class="muted">{{ t('common.loading') }}</p>

    <div v-else class="grid">
      <form class="card form" @submit.prevent="save">
        <UiField :label="t('profile.fields.handle')" for-id="handle">
          <UiTextInput id="handle" v-model="handle" placeholder="jean-dev" autocomplete="off" />
          <span class="hint">{{ t('profile.fields.handleHint') }}</span>
        </UiField>

        <UiField :label="t('profile.fields.displayName')" for-id="display-name">
          <UiTextInput id="display-name" v-model="displayName" placeholder="Jean Dev" />
        </UiField>

        <UiField :label="t('profile.fields.headline')" for-id="headline">
          <UiTextInput
            id="headline"
            v-model="headline"
            :placeholder="t('profile.fields.headlinePlaceholder')"
          />
        </UiField>

        <UiField :label="t('profile.fields.skills')" for-id="skills">
          <UiTextInput id="skills" v-model="skills" placeholder="Vue, FastAPI, DevOps" />
          <span class="hint">{{ t('profile.fields.skillsHint') }}</span>
        </UiField>

        <UiField :label="t('profile.fields.bio')" for-id="bio">
          <UiTextarea id="bio" v-model="bio" :rows="4" />
        </UiField>

        <label class="check">
          <input v-model="available" type="checkbox" />
          <span>{{ t('profile.fields.available') }}</span>
        </label>

        <div class="actions">
          <UiButton type="submit" :loading="saving" :disabled="!handle || !displayName">
            {{ t('profile.save') }}
          </UiButton>
          <span v-if="saved" class="ok" role="status">{{ t('profile.saved') }}</span>
        </div>

        <p v-if="error" class="error" role="alert">{{ error }}</p>

        <div v-if="publicUrl" class="public">
          <span class="public__label">{{ t('profile.publicLink') }}</span>
          <code class="public__url">{{ publicUrl }}</code>
          <button type="button" class="public__copy" @click="copyPublicUrl">
            {{ t('profile.copy') }}
          </button>
        </div>
      </form>

      <aside class="side">
        <ReputationCard v-if="reputation" :reputation="reputation" />
      </aside>
    </div>
  </AppShell>
</template>

<style scoped>
.head {
  margin-bottom: 2.2rem;
}
.head__title {
  margin-top: 0.7rem;
  font-size: var(--fs-display-lg);
}
.head__lead {
  margin-top: 0.6rem;
  max-width: 52ch;
  color: var(--muted-on-ink);
}
.muted {
  color: var(--muted-on-ink);
}
.grid {
  display: grid;
  gap: 1.4rem;
  align-items: start;
}
@media (min-width: 880px) {
  .grid {
    grid-template-columns: 1.4fr 1fr;
  }
}
.card {
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
  padding: clamp(1.3rem, 3vw, 1.8rem);
}
.form {
  display: grid;
  gap: 1.1rem;
}
.hint {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.check {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: var(--fs-small);
}
.actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.4rem;
}
.ok {
  font-size: var(--fs-small);
  color: var(--accent-on-ink);
}
.error {
  color: var(--danger);
  font-size: var(--fs-small);
}
.public {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.6rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line-on-ink);
}
.public__label {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted-on-ink);
}
.public__url {
  font-family: var(--font-mono);
  font-size: var(--fs-small);
}
.public__copy {
  font-size: var(--fs-small);
  color: var(--accent-on-ink);
  text-decoration: underline;
}
</style>
