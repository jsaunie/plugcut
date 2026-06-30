<script setup lang="ts">
defineProps<{ label: string; forId?: string; error?: string }>()
</script>

<template>
  <div class="ui-field">
    <label v-if="label" class="ui-field__label" :for="forId">{{ label }}</label>
    <slot />
    <p v-if="error" class="ui-field__error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.ui-field {
  display: grid;
  gap: 0.45rem;
}
.ui-field__label {
  font-size: var(--fs-small);
  font-weight: 600;
  color: var(--text-on-ink);
}
.ui-field__error {
  font-size: var(--fs-small);
  color: var(--danger);
}
</style>
