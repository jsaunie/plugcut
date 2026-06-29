<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { tm } = useI18n()
const items = computed(() => tm('marquee.items') as string[])
</script>

<template>
  <div class="marquee" role="presentation">
    <div class="marquee__track">
      <template v-for="pass in 2" :key="pass">
        <span v-for="(item, i) in items" :key="`${pass}-${i}`" class="marquee__item">
          {{ item }}
          <span class="marquee__sep" aria-hidden="true">✂</span>
        </span>
      </template>
    </div>
  </div>
</template>

<style scoped>
.marquee {
  background: var(--accent);
  color: var(--accent-ink);
  overflow: hidden;
  border-block: 1px solid var(--ink);
}
.marquee__track {
  display: flex;
  width: max-content;
  animation: scroll 38s linear infinite;
}
.marquee:hover .marquee__track {
  animation-play-state: paused;
}
.marquee__item {
  display: inline-flex;
  align-items: center;
  gap: 1.4rem;
  padding: 0.85rem 0;
  margin-right: 1.4rem;
  font-family: var(--font-mono);
  font-size: 0.84rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  white-space: nowrap;
}
.marquee__sep {
  opacity: 0.55;
}
@keyframes scroll {
  to {
    transform: translateX(-50%);
  }
}
</style>
