<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'

import AppShell from '@/features/app/AppShell.vue'
import DealStatus from '@/features/referrals/DealStatus.vue'
import { getReferral } from '@/features/referrals/api'
import type { ReferralDetail } from '@/features/referrals/types'
import { formatCurrency, formatDate } from '@/shared/format'
import { ApiError } from '@/shared/http'

const { t, locale } = useI18n()
const route = useRoute()

const deal = ref<ReferralDetail | null>(null)
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    deal.value = await getReferral(route.params.id as string)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : t('deals.errors.generic')
  } finally {
    loading.value = false
  }
})

function money(value: number, currency = 'EUR'): string {
  return formatCurrency(value, currency, locale.value)
}
function day(iso: string): string {
  return formatDate(iso, locale.value)
}
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
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in deal.schedule" :key="row.sequence">
              <td>{{ row.sequence }}</td>
              <td>{{ day(row.period_start) }}</td>
              <td>{{ day(row.due_date) }}</td>
              <td class="num">{{ money(row.expected_amount, deal.currency) }}</td>
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
</style>
