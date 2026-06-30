<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'

import AppShell from '@/features/app/AppShell.vue'
import {
  acceptReferral,
  activateReferral,
  getAgreement,
  getReferral,
  payInstallment,
  qualifyReferral,
} from '@/features/referrals/api'
import DealStatus from '@/features/referrals/DealStatus.vue'
import type { AcceptParty, ReferralDetail } from '@/features/referrals/types'
import { formatCurrency, formatDate } from '@/shared/format'
import { ApiError } from '@/shared/http'
import { UiButton } from '@/ui'

const { t, locale } = useI18n()
const route = useRoute()
const id = route.params.id as string

const deal = ref<ReferralDetail | null>(null)
const error = ref('')
const loading = ref(true)
const actionError = ref('')
const busy = ref(false)

const signedStates = ['signed', 'active', 'completed']
const canQualify = computed(() => ['sent', 'in_discussion'].includes(deal.value?.status ?? ''))
const canAccept = computed(() => deal.value?.status === 'qualified')
const canActivate = computed(() => deal.value?.status === 'signed')
const isSigned = computed(() => signedStates.includes(deal.value?.status ?? ''))

async function load(): Promise<void> {
  loading.value = true
  try {
    deal.value = await getReferral(id)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : t('deals.errors.generic')
  } finally {
    loading.value = false
  }
}

async function run(action: () => Promise<unknown>): Promise<void> {
  actionError.value = ''
  busy.value = true
  try {
    await action()
    await load()
  } catch (err) {
    actionError.value = err instanceof ApiError ? err.message : t('deals.errors.generic')
  } finally {
    busy.value = false
  }
}

const qualify = () => run(() => qualifyReferral(id))
const accept = (party: AcceptParty) => run(() => acceptReferral(id, party))
const activate = () => run(() => activateReferral(id))
const pay = (sequence: number) => run(() => payInstallment(id, sequence))

async function openAgreement(): Promise<void> {
  actionError.value = ''
  try {
    const { html } = await getAgreement(id)
    const url = URL.createObjectURL(new Blob([html], { type: 'text/html' }))
    window.open(url, '_blank')
    setTimeout(() => URL.revokeObjectURL(url), 30000)
  } catch (err) {
    actionError.value = err instanceof ApiError ? err.message : t('deals.errors.generic')
  }
}

function money(value: number, currency = 'EUR'): string {
  return formatCurrency(value, currency, locale.value)
}
function day(iso: string): string {
  return formatDate(iso, locale.value)
}

onMounted(load)
</script>

<template>
  <AppShell>
    <RouterLink to="/app" class="back">← {{ t('common.back') }}</RouterLink>

    <p v-if="loading" class="muted">{{ t('common.loading') }}</p>
    <p v-else-if="error" class="error" role="alert">{{ error }}</p>

    <template v-else-if="deal">
      <header class="dealhead">
        <div>
          <h1 class="dealhead__title">{{ deal.client_reference }}</h1>
          <p class="dealhead__placed">{{ deal.placed_person_email }}</p>
        </div>
        <DealStatus :status="deal.status" />
      </header>

      <section class="actions">
        <h2 class="section-title">{{ t('deals.actions.title') }}</h2>
        <div class="actions__row">
          <UiButton v-if="canQualify" :loading="busy" @click="qualify">
            {{ t('deals.actions.qualify') }}
          </UiButton>
          <template v-if="canAccept">
            <UiButton
              variant="ghost"
              :disabled="busy || deal.accepted_by_referrer"
              @click="accept('referrer')"
            >
              {{ deal.accepted_by_referrer ? t('deals.actions.accepted') : t('deals.actions.acceptReferrer') }}
            </UiButton>
            <UiButton
              variant="ghost"
              :disabled="busy || deal.accepted_by_placed"
              @click="accept('placed')"
            >
              {{ deal.accepted_by_placed ? t('deals.actions.accepted') : t('deals.actions.acceptPlaced') }}
            </UiButton>
          </template>
          <UiButton v-if="canActivate" :loading="busy" @click="activate">
            {{ t('deals.actions.activate') }}
          </UiButton>
          <UiButton v-if="isSigned" variant="ghost" @click="openAgreement">
            {{ t('deals.actions.viewAgreement') }}
          </UiButton>
        </div>
        <p v-if="actionError" class="error" role="alert">{{ actionError }}</p>
      </section>

      <dl class="terms">
        <div><dt>{{ t('deals.detail.dailyRate') }}</dt><dd>{{ money(deal.daily_rate, deal.currency) }}</dd></div>
        <div><dt>{{ t('deals.detail.commission') }}</dt><dd>{{ deal.commission_rate }} %</dd></div>
        <div>
          <dt>{{ t('deals.detail.duration') }}</dt>
          <dd>{{ deal.duration_months }} {{ t('deals.detail.monthsUnit') }}</dd>
        </div>
        <div><dt>{{ t('deals.detail.monthly') }}</dt><dd>{{ money(deal.monthly_expected, deal.currency) }}</dd></div>
        <div class="terms__total">
          <dt>{{ t('deals.detail.total') }}</dt>
          <dd>{{ money(deal.total_expected, deal.currency) }}</dd>
        </div>
      </dl>

      <section class="attribution">
        <h2 class="section-title">{{ t('deals.detail.attribution') }}</h2>
        <p v-if="deal.attribution_hash" class="attribution__hash">{{ deal.attribution_hash }}</p>
        <p v-else class="muted">{{ t('deals.detail.attributionNone') }}</p>
      </section>

      <section class="schedule">
        <h2 class="section-title">{{ t('deals.detail.schedule') }}</h2>
        <table class="sched">
          <thead>
            <tr>
              <th>#</th>
              <th>{{ t('deals.detail.period') }}</th>
              <th>{{ t('deals.detail.due') }}</th>
              <th class="num">{{ t('deals.detail.amount') }}</th>
              <th>{{ t('deals.detail.status') }}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in deal.schedule" :key="row.sequence">
              <td>{{ row.sequence }}</td>
              <td>{{ day(row.period_start) }}</td>
              <td>{{ day(row.due_date) }}</td>
              <td class="num">{{ money(row.expected_amount, deal.currency) }}</td>
              <td class="istatus" :class="`istatus--${row.status}`">
                {{ t(`deals.installmentStatus.${row.status}`) }}
              </td>
              <td class="num">
                <button
                  v-if="isSigned && row.status !== 'paid'"
                  class="pay"
                  :disabled="busy"
                  @click="pay(row.sequence)"
                >
                  {{ t('deals.actions.pay') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
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
.muted {
  color: var(--muted-on-ink);
}
.error {
  color: var(--danger);
  margin-top: 0.8rem;
}
.dealhead {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  margin: 1rem 0 2rem;
}
.dealhead__title {
  font-size: var(--fs-display-md);
}
.dealhead__placed {
  margin-top: 0.4rem;
  color: var(--muted-on-ink);
  font-family: var(--font-mono);
  font-size: var(--fs-small);
}
.actions {
  margin-bottom: 2.5rem;
}
.actions__row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
}
.terms {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1px;
  background: var(--line-on-ink);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 2.5rem;
}
.terms > div {
  background: var(--ink-2);
  padding: 1.1rem 1.2rem;
}
.terms dt {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted-on-ink);
}
.terms dd {
  margin-top: 0.35rem;
  font-family: var(--font-mono);
  font-weight: 700;
}
.terms__total {
  background: var(--accent) !important;
  color: var(--accent-ink);
}
.terms__total dt {
  color: rgba(11, 11, 13, 0.7);
}
.section-title {
  font-size: 1.3rem;
  margin-bottom: 1rem;
}
.attribution {
  margin-bottom: 2.5rem;
}
.attribution__hash {
  font-family: var(--font-mono);
  font-size: var(--fs-small);
  color: var(--accent-deep);
  word-break: break-all;
  padding: 0.9rem 1rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-sm);
}
.sched {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--fs-small);
}
.sched th,
.sched td {
  text-align: left;
  padding: 0.7rem 0.6rem;
  border-bottom: 1px solid var(--line-on-ink);
}
.sched th {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted-on-ink);
}
.sched .num {
  text-align: right;
  font-family: var(--font-mono);
}
.istatus {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted-on-ink);
}
.istatus--paid {
  color: var(--accent-deep);
}
.istatus--overdue {
  color: var(--danger);
}
.pay {
  padding: 0.3rem 0.8rem;
  border-radius: var(--radius-pill);
  background: var(--accent);
  color: var(--accent-ink);
  font-size: 0.78rem;
  font-weight: 600;
}
.pay:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
