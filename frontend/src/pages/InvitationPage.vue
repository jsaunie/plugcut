<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'

import LangSwitch from '@/components/shared/LangSwitch.vue'
import { getInvitation, signInvitation } from '@/features/invitation/api'
import type { PublicReferral } from '@/features/invitation/types'
import { signatureError } from '@/features/invitation/validation'
import { formatCurrency } from '@/shared/format'
import { ApiError } from '@/shared/http'
import { UiButton, UiField, UiTextInput } from '@/ui'

const { t, locale } = useI18n()
const route = useRoute()
const token = route.params.token as string

const deal = ref<PublicReferral | null>(null)
const loading = ref(true)
const invalid = ref(false)

const name = ref('')
const consent = ref(false)
const nameError = ref('')
const formError = ref('')
const submitting = ref(false)

const alreadySigned = computed(() => deal.value?.placed_signed ?? false)

function money(value: number, currency = 'EUR'): string {
  return formatCurrency(value, currency, locale.value)
}

onMounted(async () => {
  try {
    deal.value = await getInvitation(token)
  } catch {
    invalid.value = true
  } finally {
    loading.value = false
  }
})

async function sign(): Promise<void> {
  formError.value = ''
  const nameKey = signatureError(name.value)
  nameError.value = nameKey ? t(nameKey) : ''
  if (nameKey) return
  if (!consent.value) {
    formError.value = t('invitation.errors.consentRequired')
    return
  }
  submitting.value = true
  try {
    deal.value = await signInvitation(token, name.value)
  } catch (err) {
    formError.value = err instanceof ApiError ? err.message : t('invitation.errors.generic')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="inv">
    <header class="inv__top">
      <div class="container inv__top-inner">
        <RouterLink to="/" class="inv__wordmark">
          <span>Plug</span><span class="inv__cut">cut</span>
        </RouterLink>
        <LangSwitch />
      </div>
    </header>

    <main class="container inv__main">
      <p v-if="loading" class="muted">{{ t('invitation.loading') }}</p>

      <div v-else-if="invalid" class="card">
        <h1 class="card__title">{{ t('invitation.invalidTitle') }}</h1>
        <p class="muted">{{ t('invitation.invalid') }}</p>
      </div>

      <div v-else-if="deal" class="card">
        <p class="eyebrow">{{ t('invitation.eyebrow') }}</p>
        <h1 class="card__title">{{ t('invitation.heading', { referrer: deal.referrer_email }) }}</h1>
        <p class="card__lead">{{ t('invitation.subtitle', { referrer: deal.referrer_email }) }}</p>

        <dl class="terms">
          <div><dt>{{ t('invitation.client') }}</dt><dd>{{ deal.client_reference }}</dd></div>
          <div><dt>{{ t('invitation.dailyRate') }}</dt><dd>{{ money(deal.daily_rate, deal.currency) }}</dd></div>
          <div><dt>{{ t('invitation.commission') }}</dt><dd>{{ deal.commission_rate }} %</dd></div>
          <div>
            <dt>{{ t('invitation.duration') }}</dt>
            <dd>{{ deal.duration_months }} {{ t('invitation.monthsUnit') }}</dd>
          </div>
          <div class="terms__highlight">
            <dt>{{ t('invitation.monthly') }}</dt>
            <dd>{{ money(deal.monthly_expected, deal.currency) }}</dd>
          </div>
        </dl>

        <div v-if="alreadySigned" class="done">
          <span class="done__check" aria-hidden="true">✓</span>
          <div>
            <h2 class="done__title">{{ t('invitation.signedTitle') }}</h2>
            <p class="muted">{{ t('invitation.signed') }}</p>
          </div>
        </div>

        <form v-else class="form" novalidate @submit.prevent="sign">
          <UiField
            :label="t('invitation.yourName')"
            for-id="signature"
            :error="nameError || undefined"
          >
            <UiTextInput
              id="signature"
              v-model="name"
              :placeholder="t('invitation.namePlaceholder')"
              :invalid="Boolean(nameError)"
            />
          </UiField>

          <label class="consent">
            <input v-model="consent" type="checkbox" />
            <span>{{ t('invitation.consent') }}</span>
          </label>

          <p v-if="formError" class="form__error" role="alert">{{ formError }}</p>

          <UiButton type="submit" size="lg" block :loading="submitting">
            {{ t('invitation.sign') }}
          </UiButton>
        </form>
      </div>
    </main>
  </div>
</template>

<style scoped>
.inv {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.inv__top {
  border-bottom: 1px solid var(--line-on-ink);
}
.inv__top-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
}
.inv__wordmark {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.4rem;
  letter-spacing: -0.03em;
}
.inv__cut {
  color: var(--accent);
}
.inv__main {
  flex: 1;
  display: flex;
  justify-content: center;
  padding-block: clamp(2rem, 6vw, 4rem);
}
.muted {
  color: var(--muted-on-ink);
}
.card {
  width: 100%;
  max-width: 540px;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
  padding: clamp(1.6rem, 4vw, 2.6rem);
}
.eyebrow {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--accent-deep);
}
.card__title {
  margin-top: 0.8rem;
  font-size: var(--fs-display-md);
  word-break: break-word;
}
.card__lead {
  margin: 0.7rem 0 1.8rem;
  color: var(--muted-on-ink);
}
.terms {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 1px;
  background: var(--line-on-ink);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 1.8rem;
}
.terms > div {
  background: var(--ink-2);
  padding: 0.9rem 1rem;
}
.terms dt {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted-on-ink);
}
.terms dd {
  margin-top: 0.3rem;
  font-family: var(--font-mono);
  font-weight: 700;
}
.terms__highlight {
  background: var(--accent) !important;
  color: var(--accent-ink);
}
.terms__highlight dt {
  color: rgba(11, 11, 13, 0.7);
}
.form {
  display: grid;
  gap: 1.1rem;
}
.consent {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
  cursor: pointer;
}
.consent input {
  margin-top: 0.2rem;
  accent-color: var(--accent);
}
.form__error {
  color: var(--danger);
  font-size: var(--fs-small);
}
.done {
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 1.2rem;
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-sm);
}
.done__check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  flex: none;
  border-radius: 50%;
  background: var(--accent);
  color: var(--accent-ink);
  font-weight: 700;
}
.done__title {
  font-size: 1.2rem;
}
</style>
