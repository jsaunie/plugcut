<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'

import AppShell from '@/features/app/AppShell.vue'
import {
  acceptReferral,
  activateReferral,
  disputeReferral,
  getAgreement,
  getDealTimeline,
  getEvidencePack,
  getInstallmentInvoice,
  getReferral,
  payInstallment,
  qualifyReferral,
  remindInstallment,
  resolveDispute,
} from '@/features/referrals/api'
import DealStatus from '@/features/referrals/DealStatus.vue'
import type { ReferralDetail, TimelineEntry } from '@/features/referrals/types'
import { UiButton, UiField, UiTextInput } from '@/ui'
import { formatCurrency, formatDate, formatDateTime } from '@/shared/format'
import { ApiError } from '@/shared/http'

const { t, locale } = useI18n()
const route = useRoute()
const id = route.params.id as string

const deal = ref<ReferralDetail | null>(null)
const timeline = ref<TimelineEntry[]>([])
const error = ref('')
const loading = ref(true)
const actionError = ref('')
const busy = ref(false)
const signatureName = ref('')
const copied = ref(false)
const disputeReason = ref('')
const showDisputeForm = ref(false)

// A disputed deal is still sealed (just frozen), so it reads as signed for display.
const signedStates = ['signed', 'active', 'completed', 'disputed']
const isReferrer = computed(() => deal.value?.role !== 'placed')
const isFrozen = computed(() => deal.value?.status === 'disputed')
const canQualify = computed(
  () => isReferrer.value && ['sent', 'in_discussion'].includes(deal.value?.status ?? ''),
)
const canSignReferrer = computed(
  () =>
    isReferrer.value &&
    deal.value?.status === 'qualified' &&
    !deal.value?.accepted_by_referrer,
)
const canActivate = computed(() => isReferrer.value && deal.value?.status === 'signed')
const isSigned = computed(() => signedStates.includes(deal.value?.status ?? ''))
// Either party can raise a dispute on a sealed, live deal; both can see the evidence pack.
const canDispute = computed(() => isSigned.value && !isFrozen.value)
const hasEvidence = computed(() => Boolean(deal.value?.attribution_hash))
const showInvite = computed(
  () => isReferrer.value && !isSigned.value && Boolean(deal.value?.invitation_token),
)
const inviteUrl = computed(() =>
  deal.value?.invitation_token
    ? `${window.location.origin}/invitation/${deal.value.invitation_token}`
    : '',
)

async function load(): Promise<void> {
  loading.value = true
  try {
    deal.value = await getReferral(id)
    timeline.value = await getDealTimeline(id)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : t('deals.errors.generic')
  } finally {
    loading.value = false
  }
}

function dateTime(iso: string): string {
  return formatDateTime(iso, locale.value)
}

function eventLabel(entry: TimelineEntry): string {
  if (entry.type === 'payment_recorded') {
    return t('deals.timeline.events.payment_recorded', { n: entry.detail })
  }
  return t(`deals.timeline.events.${entry.type}`)
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
const signReferrer = () => run(() => acceptReferral(id, 'referrer', signatureName.value))
const activate = () => run(() => activateReferral(id))
const pay = (sequence: number) => run(() => payInstallment(id, sequence))
const remind = (sequence: number) => run(() => remindInstallment(id, sequence))
const resolve = () => run(() => resolveDispute(id))

async function submitDispute(): Promise<void> {
  await run(() => disputeReferral(id, disputeReason.value))
  if (!actionError.value) {
    disputeReason.value = ''
    showDisputeForm.value = false
  }
}

async function copyLink(): Promise<void> {
  await navigator.clipboard.writeText(inviteUrl.value)
  copied.value = true
  setTimeout(() => (copied.value = false), 2000)
}

function openHtmlInNewTab(html: string): void {
  const url = URL.createObjectURL(new Blob([html], { type: 'text/html' }))
  window.open(url, '_blank')
  setTimeout(() => URL.revokeObjectURL(url), 30000)
}

async function openAgreement(): Promise<void> {
  actionError.value = ''
  try {
    openHtmlInNewTab((await getAgreement(id)).html)
  } catch (err) {
    actionError.value = err instanceof ApiError ? err.message : t('deals.errors.generic')
  }
}

async function openInvoice(sequence: number): Promise<void> {
  actionError.value = ''
  try {
    openHtmlInNewTab((await getInstallmentInvoice(id, sequence)).html)
  } catch (err) {
    actionError.value = err instanceof ApiError ? err.message : t('deals.errors.generic')
  }
}

async function openEvidence(): Promise<void> {
  actionError.value = ''
  try {
    openHtmlInNewTab((await getEvidencePack(id)).html)
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
        <div class="dealhead__meta">
          <span class="role" :class="`role--${deal.role}`">{{ t(`deals.role.${deal.role}`) }}</span>
          <DealStatus :status="deal.status" />
        </div>
      </header>

      <div v-if="isFrozen" class="freeze" role="alert">
        <div class="freeze__body">
          <p class="freeze__title">{{ t('deals.dispute.frozenTitle') }}</p>
          <p v-if="deal.dispute_reason" class="freeze__reason">{{ deal.dispute_reason }}</p>
        </div>
        <div class="freeze__actions">
          <UiButton variant="ghost" @click="openEvidence">
            {{ t('deals.dispute.evidence') }}
          </UiButton>
          <UiButton :loading="busy" @click="resolve">{{ t('deals.dispute.resolve') }}</UiButton>
        </div>
      </div>

      <section class="actions">
        <h2 class="section-title">{{ t('deals.actions.title') }}</h2>
        <div class="actions__row">
          <UiButton v-if="canQualify" :loading="busy" @click="qualify">
            {{ t('deals.actions.qualify') }}
          </UiButton>
          <UiButton v-if="canActivate" :loading="busy" @click="activate">
            {{ t('deals.actions.activate') }}
          </UiButton>
          <UiButton v-if="isSigned" variant="ghost" @click="openAgreement">
            {{ t('deals.actions.viewAgreement') }}
          </UiButton>
          <UiButton v-if="hasEvidence && !isFrozen" variant="ghost" @click="openEvidence">
            {{ t('deals.dispute.evidence') }}
          </UiButton>
          <UiButton
            v-if="canDispute"
            variant="ghost"
            @click="showDisputeForm = !showDisputeForm"
          >
            {{ t('deals.dispute.raise') }}
          </UiButton>
        </div>

        <form
          v-if="showDisputeForm && canDispute"
          class="sign"
          @submit.prevent="submitDispute"
        >
          <p class="sign__prompt">{{ t('deals.dispute.prompt') }}</p>
          <div class="sign__row">
            <UiField :label="t('deals.dispute.reasonLabel')" for-id="dreason">
              <UiTextInput
                id="dreason"
                v-model="disputeReason"
                :placeholder="t('deals.dispute.reasonPlaceholder')"
              />
            </UiField>
            <UiButton type="submit" :loading="busy" :disabled="!disputeReason.trim()">
              {{ t('deals.dispute.submit') }}
            </UiButton>
          </div>
        </form>

        <form v-if="canSignReferrer" class="sign" @submit.prevent="signReferrer">
          <p class="sign__prompt">{{ t('deals.sign.referrerPrompt') }}</p>
          <div class="sign__row">
            <UiField :label="t('deals.sign.yourName')" for-id="rsig">
              <UiTextInput id="rsig" v-model="signatureName" :placeholder="t('deals.sign.namePlaceholder')" />
            </UiField>
            <UiButton type="submit" :loading="busy" :disabled="!signatureName.trim()">
              {{ t('deals.sign.signAsReferrer') }}
            </UiButton>
          </div>
        </form>
        <p v-else-if="deal.accepted_by_referrer && !isSigned" class="signed-note">
          {{ t('deals.sign.referrerSigned') }}
        </p>

        <p v-if="actionError" class="error" role="alert">{{ actionError }}</p>
      </section>

      <section v-if="showInvite" class="invite">
        <h2 class="section-title">{{ t('deals.invite.title') }}</h2>
        <p class="muted invite__lead">{{ t('deals.invite.subtitle') }}</p>
        <div class="invite__row">
          <input class="invite__url" :value="inviteUrl" readonly @focus="(e) => (e.target as HTMLInputElement).select()" />
          <UiButton variant="ghost" @click="copyLink">
            {{ copied ? t('deals.invite.copied') : t('deals.invite.copy') }}
          </UiButton>
        </div>
        <p class="invite__status">
          {{ deal.accepted_by_placed ? t('deals.invite.placedSigned') : t('deals.invite.placedPending') }}
        </p>
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
                <span v-if="isSigned" class="rowactions">
                  <button class="rowactions__link" @click="openInvoice(row.sequence)">
                    {{ t('deals.actions.invoice') }}
                  </button>
                  <button
                    v-if="isReferrer && !isFrozen && row.status !== 'paid'"
                    class="rowactions__link"
                    :disabled="busy"
                    :title="row.last_reminded_at ? t('deals.actions.remindedOn', { date: day(row.last_reminded_at) }) : ''"
                    @click="remind(row.sequence)"
                  >
                    {{ row.last_reminded_at ? t('deals.actions.remindAgain') : t('deals.actions.remind') }}
                  </button>
                  <button
                    v-if="isReferrer && !isFrozen && row.status !== 'paid'"
                    class="pay"
                    :disabled="busy"
                    @click="pay(row.sequence)"
                  >
                    {{ t('deals.actions.pay') }}
                  </button>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section v-if="timeline.length" class="history">
        <h2 class="section-title">{{ t('deals.timeline.title') }}</h2>
        <ol class="tl">
          <li v-for="(entry, i) in timeline" :key="i" class="tl__item">
            <time class="tl__time">{{ dateTime(entry.at) }}</time>
            <div class="tl__body">
              <span class="tl__label">{{ eventLabel(entry) }}</span>
              <span
                v-if="entry.detail && entry.type !== 'payment_recorded'"
                class="tl__detail"
              >
                {{ entry.detail }}
              </span>
            </div>
          </li>
        </ol>
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
.dealhead__meta {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}
.role {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-pill);
}
.role--referrer {
  background: rgba(216, 255, 54, 0.14);
  color: var(--accent-deep);
}
.role--placed {
  background: var(--ink-3);
  color: var(--muted-on-ink);
}
.freeze {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2.2rem;
  padding: 1.1rem 1.3rem;
  border: 1px solid var(--danger);
  border-radius: var(--radius);
  background: rgba(255, 92, 92, 0.08);
}
.freeze__title {
  font-weight: 700;
  color: var(--danger);
}
.freeze__reason {
  margin-top: 0.3rem;
  color: var(--text-on-ink);
  font-size: var(--fs-small);
}
.freeze__actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}
.actions {
  margin-bottom: 2.5rem;
}
.actions__row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
}
.sign {
  margin-top: 1.2rem;
  padding: 1.2rem;
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-sm);
  max-width: 480px;
}
.sign__prompt {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
  margin-bottom: 0.8rem;
}
.sign__row {
  display: flex;
  gap: 0.7rem;
  align-items: flex-end;
}
.sign__row > :first-child {
  flex: 1;
}
.signed-note {
  margin-top: 1rem;
  font-size: var(--fs-small);
  color: var(--accent-deep);
}
.invite {
  margin-bottom: 2.5rem;
}
.invite__lead {
  margin-bottom: 1rem;
  max-width: 52ch;
}
.invite__row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}
.invite__url {
  flex: 1;
  min-width: 240px;
  padding: 0.7rem 0.9rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-sm);
  color: var(--text-on-ink);
  font-family: var(--font-mono);
  font-size: var(--fs-small);
}
.invite__status {
  margin-top: 0.9rem;
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
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
.history {
  margin-top: 2.5rem;
}
.tl {
  list-style: none;
  display: grid;
  border-left: 1px solid var(--line-on-ink);
}
.tl__item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1rem;
  padding: 0.6rem 0 0.6rem 1.2rem;
}
.tl__time {
  font-family: var(--font-mono);
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
  white-space: nowrap;
}
.tl__body {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: baseline;
}
.tl__label {
  font-weight: 600;
}
.tl__detail {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
  font-family: var(--font-mono);
}
@media (max-width: 520px) {
  .tl__item {
    grid-template-columns: 1fr;
    gap: 0.2rem;
  }
}
.rowactions {
  display: inline-flex;
  gap: 0.6rem;
  align-items: center;
  justify-content: flex-end;
}
.rowactions__link {
  font-size: 0.78rem;
  color: var(--accent-deep);
  text-decoration: underline;
}
.rowactions__link:hover {
  color: var(--accent);
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
