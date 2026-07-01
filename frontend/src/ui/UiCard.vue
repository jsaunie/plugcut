<script setup lang="ts">
withDefaults(defineProps<{ tone?: 'ink' | 'paper'; hover?: boolean }>(), {
  tone: 'ink',
  hover: false,
})
</script>

<template>
  <div class="ui-card" :class="[`ui-card--${tone}`, { 'ui-card--hover': hover }]">
    <slot />
  </div>
</template>

<style scoped>
.ui-card {
  border-radius: var(--radius);
  padding: 1.9rem 1.7rem 2rem;
  border: 1px solid var(--line-on-ink);
  box-shadow: var(--shadow-card);
  transition:
    transform var(--dur) ease,
    border-color var(--dur) ease,
    box-shadow var(--dur) ease,
    background var(--dur) ease;
}
/* Default surface: a white card floating on the light canvas. */
.ui-card--ink {
  background: var(--ink-2);
}
/* Warm ticket-paper surface, for the signature stub/pillar treatment. */
.ui-card--paper {
  background: var(--paper);
  border-color: var(--line-on-paper);
}
.ui-card--hover:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lift);
}
</style>
