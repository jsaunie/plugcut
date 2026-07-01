<script setup lang="ts">
// Section label. Plain mono uppercase text, no decorative dot/pastille.
withDefaults(defineProps<{ tone?: 'muted' | 'accent' | 'paper' | 'solid' }>(), {
  tone: 'muted',
})
</script>

<template>
  <p class="ui-eyebrow" :class="`ui-eyebrow--${tone}`"><slot /></p>
</template>

<style scoped>
.ui-eyebrow {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  letter-spacing: 0.22em;
  text-transform: uppercase;
}
.ui-eyebrow--muted {
  color: var(--muted-on-ink);
}
.ui-eyebrow--accent {
  color: var(--accent-on-ink);
}
.ui-eyebrow--paper {
  color: var(--text-on-paper);
  opacity: 0.7;
}
.ui-eyebrow--solid {
  color: var(--text-on-solid);
  opacity: 0.6;
}
</style>
