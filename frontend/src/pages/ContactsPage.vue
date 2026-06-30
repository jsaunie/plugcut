<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import AppShell from '@/features/app/AppShell.vue'
import { useContactsStore } from '@/features/contacts/store'
import { UiButton } from '@/ui'

const { t } = useI18n()
const store = useContactsStore()
const contacts = computed(() => store.contacts)

onMounted(() => {
  if (!store.loaded) void store.fetchAll()
})
</script>

<template>
  <AppShell>
    <div class="head">
      <div>
        <h1 class="head__title">{{ t('contacts.title') }}</h1>
        <p class="head__lead">{{ t('contacts.lead') }}</p>
      </div>
      <UiButton to="/app/contacts/nouveau">{{ t('contacts.add') }}</UiButton>
    </div>

    <p v-if="store.loading && !contacts.length" class="muted">{{ t('common.loading') }}</p>

    <div v-else-if="!contacts.length" class="empty">
      <p>{{ t('contacts.empty') }}</p>
      <UiButton to="/app/contacts/nouveau">{{ t('contacts.add') }}</UiButton>
    </div>

    <ul v-else class="list">
      <li v-for="contact in contacts" :key="contact.id">
        <RouterLink :to="`/app/contacts/${contact.id}`" class="card">
          <div class="card__main">
            <span class="card__name">{{ contact.full_name }}</span>
            <span v-if="contact.headline" class="card__headline">{{ contact.headline }}</span>
            <span v-if="contact.company" class="card__company">{{ contact.company }}</span>
          </div>
          <div class="card__side">
            <span class="card__kind">{{ t(`contacts.kind.${contact.kind}`) }}</span>
            <ul v-if="contact.tags.length" class="tags">
              <li v-for="tag in contact.tags.slice(0, 4)" :key="tag" class="tag">{{ tag }}</li>
            </ul>
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
  max-width: 52ch;
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
.list {
  list-style: none;
  display: grid;
  gap: 0.9rem;
}
.card {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  padding: 1.2rem 1.5rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius);
  transition:
    border-color var(--dur) ease,
    transform var(--dur) ease;
}
.card:hover {
  border-color: var(--text-on-ink);
  transform: translateY(-2px);
}
.card__main {
  display: grid;
  gap: 0.2rem;
}
.card__name {
  font-weight: 600;
}
.card__headline {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
}
.card__company {
  font-size: var(--fs-small);
  color: var(--muted-on-ink);
  font-family: var(--font-mono);
}
.card__side {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.card__kind {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted-on-ink);
}
.tags {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.tag {
  font-size: 0.72rem;
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-pill);
  background: var(--ink-3);
  color: var(--text-on-ink);
}
</style>
