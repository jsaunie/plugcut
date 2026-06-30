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
  transition:
    transform var(--dur) ease,
    border-color var(--dur) ease,
    background var(--dur) ease;
}
.ui-card--ink {
  background: var(--ink-2);
}
.ui-card--paper {
  background: rgba(255, 255, 255, 0.4);
  border-color: var(--line-on-paper);
}
.ui-card--hover:hover {
  transform: translateY(-4px);
}
.ui-card--ink.ui-card--hover:hover {
  border-color: var(--text-on-ink);
}
.ui-card--paper.ui-card--hover:hover {
  border-color: var(--text-on-paper);
}
</style>
