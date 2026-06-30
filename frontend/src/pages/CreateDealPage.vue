<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'

import AppShell from '@/features/app/AppShell.vue'
import { emailError } from '@/features/auth/validation'
import { useContactsStore } from '@/features/contacts/store'
import { useReferralsStore } from '@/features/referrals/store'
import { formatCurrency } from '@/shared/format'
import { ApiError } from '@/shared/http'
import { UiButton, UiField, UiTextInput } from '@/ui'

const { t, locale } = useI18n()
const router = useRouter()
const store = useReferralsStore()
const contactsStore = useContactsStore()

const selectedContactId = ref('')
const pickableContacts = computed(() => contactsStore.contacts.filter((c) => c.email))

onMounted(() => {
  if (!contactsStore.loaded) void contactsStore.fetchAll()
})

function applyContact(): void {
  const contact = contactsStore.contacts.find((c) => c.id === selectedContactId.value)
  if (!contact?.email) return
  form.placed_person_email = contact.email
  if (!form.client_reference.trim()) {
    form.client_reference = contact.company || contact.full_name
  }
  errors.email = undefined
}

const form = reactive({
  placed_person_email: '',
  client_reference: '',
  daily_rate: '500',
  commission_rate: '10',
  duration_months: '12',
  days_per_period: '20',
})
const errors = reactive<{ email?: string; client?: string }>({})
const formError = ref('')
const loading = ref(false)

const monthly = computed(
  () => Number(form.daily_rate) * Number(form.days_per_period) * (Number(form.commission_rate) / 100),
)
const total = computed(() => monthly.value * Number(form.duration_months))

function money(value: number): string {
  return formatCurrency(Number.isFinite(value) ? value : 0, 'EUR', locale.value)
}

function validate(): boolean {
  errors.email = emailError(form.placed_person_email) ?? undefined
  errors.client = form.client_reference.trim() ? undefined : 'deals.errors.clientRequired'
  return !errors.email && !errors.client
}

async function submit(): Promise<void> {
  formError.value = ''
  if (!validate()) return
  loading.value = true
  try {
    const deal = await store.create({
      placed_person_email: form.placed_person_email,
      client_reference: form.client_reference,
      daily_rate: Number(form.daily_rate),
      commission_rate: Number(form.commission_rate),
      duration_months: Number(form.duration_months),
      days_per_period: Number(form.days_per_period),
    })
    await router.push(`/app/deals/${deal.id}`)
  } catch (err) {
    formError.value = err instanceof ApiError ? err.message : t('deals.errors.generic')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppShell>
    <RouterLink to="/app" class="back">← {{ t('common.back') }}</RouterLink>
    <h1 class="title">{{ t('deals.create.title') }}</h1>
    <p class="subtitle">{{ t('deals.create.subtitle') }}</p>

    <div class="layout">
      <form class="form" novalidate @submit.prevent="submit">
        <UiField v-if="pickableContacts.length" :label="t('deals.create.fromNetwork')" for-id="contact">
          <select
            id="contact"
            v-model="selectedContactId"
            class="picker"
            @change="applyContact"
          >
            <option value="">{{ t('deals.create.pickContact') }}</option>
            <option v-for="c in pickableContacts" :key="c.id" :value="c.id">
              {{ c.company ? `${c.full_name} · ${c.company}` : c.full_name }}
            </option>
          </select>
        </UiField>

        <UiField
          :label="t('deals.create.placedEmail')"
          for-id="placed"
          :error="errors.email ? t(errors.email) : undefined"
        >
          <UiTextInput
            id="placed"
            v-model="form.placed_person_email"
            type="email"
            autocomplete="off"
            :placeholder="t('auth.emailPlaceholder')"
            :invalid="Boolean(errors.email)"
          />
        </UiField>

        <UiField
          :label="t('deals.create.clientRef')"
          for-id="client"
          :error="errors.client ? t(errors.client) : undefined"
        >
          <UiTextInput id="client" v-model="form.client_reference" :invalid="Boolean(errors.client)" />
        </UiField>

        <div class="grid">
          <UiField :label="t('deals.create.dailyRate')" for-id="rate">
            <UiTextInput id="rate" v-model="form.daily_rate" type="number" />
          </UiField>
          <UiField :label="t('deals.create.commissionRate')" for-id="commission">
            <UiTextInput id="commission" v-model="form.commission_rate" type="number" />
          </UiField>
          <UiField :label="t('deals.create.durationMonths')" for-id="duration">
            <UiTextInput id="duration" v-model="form.duration_months" type="number" />
          </UiField>
          <UiField :label="t('deals.create.daysPerPeriod')" for-id="days">
            <UiTextInput id="days" v-model="form.days_per_period" type="number" />
          </UiField>
        </div>

        <p v-if="formError" class="form__error" role="alert">{{ formError }}</p>

        <div class="actions">
          <UiButton type="submit" size="lg" :loading="loading">{{ t('deals.create.submit') }}</UiButton>
          <UiButton to="/app" variant="ghost" size="lg">{{ t('common.cancel') }}</UiButton>
        </div>
      </form>

      <aside class="preview">
        <p class="preview__label">{{ t('deals.create.previewMonthly') }}</p>
        <strong class="preview__monthly">{{ money(monthly) }}</strong>
        <p class="preview__label">{{ t('deals.create.previewTotal') }}</p>
        <strong class="preview__total">{{ money(total) }}</strong>
        <p class="preview__note">{{ t('deals.create.previewNote') }}</p>
      </aside>
    </div>
  </AppShell>
</template>

<style scoped>
.back {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.back:hover {
  color: var(--accent);
}
.title {
  margin-top: 1rem;
  font-size: var(--fs-display-md);
}
.subtitle {
  margin: 0.6rem 0 2rem;
  color: var(--muted-on-ink);
  max-width: 50ch;
}
.layout {
  display: grid;
  gap: 2rem;
  align-items: start;
}
.form {
  display: grid;
  gap: 1.2rem;
}
.grid {
  display: grid;
  gap: 1.2rem;
  grid-template-columns: repeat(2, 1fr);
}
.picker {
  width: 100%;
  padding: 0.8rem 1rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-sm);
  color: var(--text-on-ink);
  font: inherit;
  transition: border-color var(--dur-fast) ease;
}
.picker:focus {
  outline: none;
  border-color: var(--accent);
}
.form__error {
  color: var(--danger);
  font-size: var(--fs-small);
}
.actions {
  display: flex;
  gap: 0.8rem;
}
.preview {
  display: grid;
  gap: 0.3rem;
  padding: 1.6rem;
  background: var(--accent);
  color: var(--accent-ink);
  border-radius: var(--radius);
}
.preview__label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.75;
  margin-top: 0.6rem;
}
.preview__monthly {
  font-family: var(--font-display);
  font-size: 1.9rem;
  line-height: 1.1;
}
.preview__total {
  font-family: var(--font-display);
  font-size: 2.6rem;
  line-height: 1.1;
}
.preview__note {
  margin-top: 0.8rem;
  font-size: 0.74rem;
  opacity: 0.72;
}
@media (min-width: 860px) {
  .layout {
    grid-template-columns: 1.4fr 0.85fr;
  }
}
</style>
