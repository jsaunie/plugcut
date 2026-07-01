<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import AppShell from '@/features/app/AppShell.vue'
import { changeEmail, changePassword, deleteAccount } from '@/features/account/api'
import { useAuthStore } from '@/features/auth/store'
import { ApiError } from '@/shared/http'
import { UiButton, UiEyebrow, UiField, UiTextInput } from '@/ui'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()

// --- Change email ---
const newEmail = ref('')
const emailPassword = ref('')
const emailBusy = ref(false)
const emailMsg = ref('')
const emailErr = ref('')

async function submitEmail(): Promise<void> {
  emailMsg.value = ''
  emailErr.value = ''
  emailBusy.value = true
  try {
    await changeEmail(newEmail.value.trim(), emailPassword.value)
    await auth.fetchMe()
    emailMsg.value = t('settings.email.done')
    newEmail.value = ''
    emailPassword.value = ''
  } catch (err) {
    emailErr.value = err instanceof ApiError ? err.message : t('settings.genericError')
  } finally {
    emailBusy.value = false
  }
}

// --- Change password ---
const currentPassword = ref('')
const nextPassword = ref('')
const confirmPassword = ref('')
const pwBusy = ref(false)
const pwMsg = ref('')
const pwErr = ref('')

async function submitPassword(): Promise<void> {
  pwMsg.value = ''
  pwErr.value = ''
  if (nextPassword.value !== confirmPassword.value) {
    pwErr.value = t('settings.password.mismatch')
    return
  }
  pwBusy.value = true
  try {
    await changePassword(currentPassword.value, nextPassword.value)
    pwMsg.value = t('settings.password.done')
    currentPassword.value = ''
    nextPassword.value = ''
    confirmPassword.value = ''
  } catch (err) {
    pwErr.value = err instanceof ApiError ? err.message : t('settings.genericError')
  } finally {
    pwBusy.value = false
  }
}

// --- Delete account ---
const showDelete = ref(false)
const deletePassword = ref('')
const deleteBusy = ref(false)
const deleteErr = ref('')

async function submitDelete(): Promise<void> {
  deleteErr.value = ''
  deleteBusy.value = true
  try {
    await deleteAccount(deletePassword.value)
    auth.logout()
    await router.push('/')
  } catch (err) {
    deleteErr.value = err instanceof ApiError ? err.message : t('settings.genericError')
    deleteBusy.value = false
  }
}
</script>

<template>
  <AppShell>
    <div class="head">
      <UiEyebrow>{{ t('settings.eyebrow') }}</UiEyebrow>
      <h1 class="head__title">{{ t('settings.title') }}</h1>
    </div>

    <div class="grid">
      <form class="card" @submit.prevent="submitEmail">
        <h2 class="card__title">{{ t('settings.email.title') }}</h2>
        <p class="card__current">
          {{ t('settings.email.current') }} <strong>{{ auth.user?.email }}</strong>
        </p>
        <UiField :label="t('settings.email.new')" for-id="new-email">
          <UiTextInput id="new-email" v-model="newEmail" type="email" autocomplete="off" />
        </UiField>
        <UiField :label="t('settings.currentPassword')" for-id="email-pw">
          <UiTextInput id="email-pw" v-model="emailPassword" type="password" autocomplete="off" />
        </UiField>
        <div class="row">
          <UiButton type="submit" :loading="emailBusy" :disabled="!newEmail || !emailPassword">
            {{ t('settings.email.save') }}
          </UiButton>
          <span v-if="emailMsg" class="ok" role="status">{{ emailMsg }}</span>
        </div>
        <p v-if="emailErr" class="err" role="alert">{{ emailErr }}</p>
      </form>

      <form class="card" @submit.prevent="submitPassword">
        <h2 class="card__title">{{ t('settings.password.title') }}</h2>
        <UiField :label="t('settings.currentPassword')" for-id="cur-pw">
          <UiTextInput id="cur-pw" v-model="currentPassword" type="password" autocomplete="off" />
        </UiField>
        <UiField :label="t('settings.password.new')" for-id="new-pw">
          <UiTextInput id="new-pw" v-model="nextPassword" type="password" autocomplete="new-password" />
          <span class="hint">{{ t('settings.password.hint') }}</span>
        </UiField>
        <UiField :label="t('settings.password.confirm')" for-id="conf-pw">
          <UiTextInput id="conf-pw" v-model="confirmPassword" type="password" autocomplete="new-password" />
        </UiField>
        <div class="row">
          <UiButton
            type="submit"
            :loading="pwBusy"
            :disabled="!currentPassword || !nextPassword || !confirmPassword"
          >
            {{ t('settings.password.save') }}
          </UiButton>
          <span v-if="pwMsg" class="ok" role="status">{{ pwMsg }}</span>
        </div>
        <p v-if="pwErr" class="err" role="alert">{{ pwErr }}</p>
      </form>
    </div>

    <section class="danger">
      <h2 class="danger__title">{{ t('settings.delete.title') }}</h2>
      <p class="danger__lead">{{ t('settings.delete.lead') }}</p>

      <UiButton v-if="!showDelete" variant="ghost" class="danger__trigger" @click="showDelete = true">
        {{ t('settings.delete.trigger') }}
      </UiButton>

      <form v-else class="danger__form" @submit.prevent="submitDelete">
        <p class="danger__warn">{{ t('settings.delete.warn') }}</p>
        <UiField :label="t('settings.currentPassword')" for-id="del-pw">
          <UiTextInput id="del-pw" v-model="deletePassword" type="password" autocomplete="off" />
        </UiField>
        <div class="row">
          <button type="submit" class="danger__confirm" :disabled="!deletePassword || deleteBusy">
            {{ t('settings.delete.confirm') }}
          </button>
          <button type="button" class="danger__cancel" @click="showDelete = false">
            {{ t('settings.delete.cancel') }}
          </button>
        </div>
        <p v-if="deleteErr" class="err" role="alert">{{ deleteErr }}</p>
      </form>
    </section>
  </AppShell>
</template>

<style scoped>
.head {
  margin-bottom: 2rem;
}
.head__title {
  margin-top: 0.7rem;
  font-size: var(--fs-display-lg);
}
.grid {
  display: grid;
  gap: 1.4rem;
  align-items: start;
}
@media (min-width: 820px) {
  .grid {
    grid-template-columns: 1fr 1fr;
  }
}
.card {
  display: grid;
  gap: 1rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
  padding: clamp(1.3rem, 3vw, 1.7rem);
}
.card__title {
  font-size: var(--fs-title);
}
.card__current {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.hint {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.row {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.ok {
  font-size: var(--fs-small);
  color: var(--accent-on-ink);
}
.err {
  font-size: var(--fs-small);
  color: var(--danger);
}
.danger {
  margin-top: 2.2rem;
  padding: clamp(1.3rem, 3vw, 1.7rem);
  border: 1px solid color-mix(in srgb, var(--danger) 45%, var(--line-on-ink));
  border-radius: var(--radius);
  background: color-mix(in srgb, var(--danger) 5%, var(--ink-2));
}
.danger__title {
  font-size: var(--fs-title);
  color: var(--danger);
}
.danger__lead {
  margin-top: 0.5rem;
  max-width: 56ch;
  color: var(--muted-on-ink);
  font-size: var(--fs-small);
}
.danger__trigger {
  margin-top: 1rem;
}
.danger__form {
  margin-top: 1.2rem;
  display: grid;
  gap: 1rem;
  max-width: 30rem;
}
.danger__warn {
  font-weight: 600;
  color: var(--danger);
}
.danger__confirm {
  padding: 0.7rem 1.2rem;
  border-radius: var(--radius-btn, 14px);
  background: var(--danger);
  color: #fff;
  font-weight: 600;
}
.danger__confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.danger__cancel {
  color: var(--muted-on-ink);
  text-decoration: underline;
  font-size: var(--fs-small);
}
</style>
