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

onMounted(() => {
  if (!store.loaded) void store.fetchAll()
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
</style>
