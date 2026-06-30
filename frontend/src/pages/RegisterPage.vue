<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'

import AuthShell from '@/features/auth/AuthShell.vue'
import { useAuthStore } from '@/features/auth/store'
import { emailError, passwordError } from '@/features/auth/validation'
import { ApiError } from '@/shared/http'
import { UiButton, UiField, UiTextInput } from '@/ui'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const errors = ref<{ email?: string; password?: string }>({})
const formError = ref('')
const loading = ref(false)

function validate(): boolean {
  const e = emailError(email.value)
  const p = passwordError(password.value)
  errors.value = { email: e ?? undefined, password: p ?? undefined }
  return !e && !p
}

async function submit(): Promise<void> {
  formError.value = ''
  if (!validate()) return
  loading.value = true
  try {
    await auth.register(email.value, password.value)
    await router.push('/app')
  } catch (err) {
    formError.value = err instanceof ApiError ? err.message : t('auth.errors.generic')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthShell :title="t('auth.registerTitle')" :subtitle="t('auth.registerSubtitle')">
    <form class="auth-form" novalidate @submit.prevent="submit">
      <UiField
        :label="t('auth.email')"
        for-id="email"
        :error="errors.email ? t(errors.email) : undefined"
      >
        <UiTextInput
          id="email"
          v-model="email"
          type="email"
          autocomplete="email"
          :placeholder="t('auth.emailPlaceholder')"
          :invalid="Boolean(errors.email)"
        />
      </UiField>

      <UiField
        :label="t('auth.password')"
        for-id="password"
        :error="errors.password ? t(errors.password) : undefined"
      >
        <UiTextInput
          id="password"
          v-model="password"
          type="password"
          autocomplete="new-password"
          :invalid="Boolean(errors.password)"
        />
        <p v-if="!errors.password" class="auth-form__hint">{{ t('auth.passwordHint') }}</p>
      </UiField>

      <p v-if="formError" class="auth-form__error" role="alert">{{ formError }}</p>

      <UiButton type="submit" size="lg" block :loading="loading">
        {{ t('auth.submitRegister') }}
      </UiButton>
    </form>

    <p class="auth-form__switch">
      {{ t('auth.toLogin') }}
      <RouterLink to="/connexion">{{ t('auth.toLoginLink') }}</RouterLink>
    </p>
  </AuthShell>
</template>

<style scoped>
.auth-form {
  display: grid;
  gap: 1.2rem;
}
.auth-form__error {
  color: var(--danger);
  font-size: var(--fs-small);
}
.auth-form__hint {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.auth-form__switch {
  margin-top: 1.6rem;
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.auth-form__switch a {
  color: var(--accent);
}
</style>
