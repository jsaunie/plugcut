<script setup lang="ts">
defineProps<{ id?: string; placeholder?: string; rows?: number; invalid?: boolean }>()

const model = defineModel<string>({ default: '' })
</script>

<template>
  <textarea
    :id="id"
    v-model="model"
    class="ui-textarea"
    :class="{ 'ui-textarea--invalid': invalid }"
    :placeholder="placeholder"
    :rows="rows ?? 4"
  />
</template>

<style scoped>
.ui-textarea {
  width: 100%;
  padding: 0.8rem 1rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-sm);
  color: var(--text-on-ink);
  resize: vertical;
  font-family: inherit;
  transition:
    border-color var(--dur-fast) ease,
    box-shadow var(--dur-fast) ease;
}
.ui-textarea::placeholder {
  color: var(--muted-on-ink);
}
.ui-textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 18%, transparent);
}
.ui-textarea--invalid {
  border-color: var(--danger);
}
</style>
