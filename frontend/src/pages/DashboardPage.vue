<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import AppShell from '@/features/app/AppShell.vue'
import DealStatus from '@/features/referrals/DealStatus.vue'
import { useReferralsStore } from '@/features/referrals/store'
import { formatCurrency } from '@/shared/format'
import { UiButton } from '@/ui'

const { t, locale } = useI18n()
const store = useReferralsStore()
const deals = computed(() => store.deals)
const stats = computed(() => store.stats)

onMounted(() => {
  if (!store.loaded) void store.fetchAll()
  void store.fetchStats()
})

function money(amount: number, currency: string): string {
  return formatCurrency(amount, currency, locale.value)
}
</script>

<template>
  <AppShell>
    <div class="head">
      <div>
        <h1 class="head__title">{{ t('dashboard.title') }}</h1>
        <p class="head__lead">{{ t('dashboard.lead') }}</p>
      </div>
      <UiButton to="/app/deals/nouveau">{{ t('dashboard.newDeal') }}</UiButton>
    </div>

    <section v-if="stats && deals.length" class="stats" :aria-label="t('stats.title')">
      <div class="kpi kpi--accent">
        <span class="kpi__label">{{ t('stats.pipeline') }}</span>
        <strong class="kpi__value">{{ money(stats.pipeline_expected, stats.currency) }}</strong>
      </div>
      <div class="kpi">
        <span class="kpi__label">{{ t('stats.collected') }}</span>
        <strong class="kpi__value">{{ money(stats.collected, stats.currency) }}</strong>
      </div>
      <div class="kpi">
        <span class="kpi__label">{{ t('stats.outstanding') }}</span>
        <strong class="kpi__value">{{ money(stats.outstanding, stats.currency) }}</strong>
        <span v-if="stats.overdue > 0" class="kpi__note kpi__note--danger">
          {{ t('stats.overdue', { amount: money(stats.overdue, stats.currency) }) }}
        </span>
      </div>
      <div class="kpi">
        <span class="kpi__label">{{ t('stats.runRate') }}</span>
        <strong class="kpi__value">{{ money(stats.monthly_run_rate, stats.currency) }}</strong>
        <span class="kpi__note">
          {{ t('stats.deals', { total: stats.total_deals, active: stats.active_deals }) }}
        </span>
      </div>
    </section>

    <p v-if="store.loading && !deals.length" class="muted">{{ t('common.loading') }}</p>

    <div v-else-if="!deals.length" class="empty">
      <span class="empty__glyph" aria-hidden="true">✂</span>
      <p>{{ t('dashboard.empty') }}</p>
      <UiButton to="/app/deals/nouveau">{{ t('dashboard.newDeal') }}</UiButton>
    </div>

    <ul v-else class="deals">
      <li v-for="deal in deals" :key="deal.id">
        <RouterLink :to="`/app/deals/${deal.id}`" class="deal">
          <div class="deal__main">
            <span class="deal__client">{{ deal.client_reference }}</span>
            <span class="deal__placed">{{ deal.placed_person_email }}</span>
          </div>
          <div class="deal__meta">
            <span class="deal__amount">
              {{ money(deal.monthly_expected, deal.currency) }}
              <span class="deal__per">{{ t('deals.list.perMonth') }}</span>
            </span>
            <span class="deal__role" :class="`deal__role--${deal.role}`">
              {{ t(`deals.role.${deal.role}`) }}
            </span>
            <DealStatus :status="deal.status" />
          </div>
        </RouterLink>
      </li>
    </ul>
  </AppShell>
</template>

<style scoped>
.head {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 2.5rem;
}
.head__title {
  font-size: var(--fs-display-lg);
}
.head__lead {
  margin-top: 0.7rem;
  color: var(--muted-on-ink);
  max-width: 50ch;
}
.muted {
  color: var(--muted-on-ink);
}
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2.5rem;
}
.kpi {
  display: grid;
  gap: 0.4rem;
  align-content: start;
  padding: 1.3rem 1.4rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
}
.kpi--accent {
  background: var(--accent);
  color: var(--accent-ink);
  border-color: var(--accent);
}
.kpi__label {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.7;
}
.kpi__value {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 3vw, 2rem);
  line-height: 1.1;
}
.kpi__note {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.kpi__note--danger {
  color: var(--danger);
}
.empty {
  display: grid;
  justify-items: start;
  gap: 1rem;
  padding: clamp(2rem, 5vw, 3.5rem);
  border: 1px dashed var(--line-on-ink);
  border-radius: var(--radius);
  color: var(--muted-on-ink);
}
.empty__glyph {
  font-size: 1.8rem;
}
.deals {
  list-style: none;
  display: grid;
  gap: 0.9rem;
}
.deal {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
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
.deal:hover {
  border-color: var(--text-on-ink);
  transform: translateY(-2px);
}
.deal__main {
  display: grid;
  gap: 0.2rem;
}
.deal__client {
  font-weight: 600;
}
.deal__placed {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.deal__meta {
  display: flex;
  align-items: center;
  gap: 1.3rem;
}
.deal__amount {
  font-family: var(--font-mono);
  font-weight: 700;
}
.deal__per {
  font-weight: 400;
  color: var(--muted-on-ink);
  font-size: var(--fs-small);
}
.deal__role {
  font-family: var(--font-mono);
  font-size: 0.66rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.22rem 0.55rem;
  border-radius: var(--radius-pill);
}
.deal__role--referrer {
  background: rgba(216, 255, 54, 0.14);
  color: var(--accent-deep);
}
.deal__role--placed {
  background: var(--ink-3);
  color: var(--muted-on-ink);
}
</style>
