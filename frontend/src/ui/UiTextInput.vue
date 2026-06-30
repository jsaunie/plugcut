<script setup lang="ts">
defineProps<{
  id?: string
  type?: string
  placeholder?: string
  autocomplete?: string
  invalid?: boolean
  disabled?: boolean
}>()

const model = defineModel<string>({ default: '' })
</script>

<template>
  <input
    :id="id"
    v-model="model"
    class="ui-input"
    :class="{ 'ui-input--invalid': invalid }"
    :type="type ?? 'text'"
    :placeholder="placeholder"
    :autocomplete="autocomplete"
    :disabled="disabled"
    :aria-invalid="invalid || undefined"
  />
</template>

<style scoped>
.ui-input {
  width: 100%;
  padding: 0.8rem 1rem;
  background: var(--ink-2);
  border: 1px solid var(--line-on-ink);
  border-radius: var(--radius-sm);
  color: var(--text-on-ink);
  transition:
    border-color var(--dur-fast) ease,
    box-shadow var(--dur-fast) ease;
}
.ui-input::placeholder {
  color: var(--muted-on-ink);
}
.ui-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(216, 255, 54, 0.18);
}
.ui-input--invalid {
  border-color: var(--danger);
}
.ui-input--invalid:focus {
  box-shadow: 0 0 0 3px rgba(255, 92, 92, 0.2);
}
.ui-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
