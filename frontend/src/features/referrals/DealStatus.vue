<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{ status: string }>()

const { t } = useI18n()
</script>

<template>
  <span class="status" :class="`status--${status}`">{{ t(`deals.status.${status}`) }}</span>
</template>

<style scoped>
.status {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-pill);
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  background: var(--ink-3);
  color: var(--muted-on-ink);
}
.status--qualified {
  background: rgba(216, 255, 54, 0.14);
  color: var(--accent-deep);
}
.status--signed,
.status--active {
  background: var(--accent);
  color: var(--accent-ink);
}
.status--completed {
  background: var(--ink-3);
  color: var(--text-on-ink);
}
.status--cancelled,
.status--disputed {
  background: rgba(255, 92, 92, 0.16);
  color: var(--danger);
}
</style>
