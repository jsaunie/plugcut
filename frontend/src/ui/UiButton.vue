<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = withDefaults(
  defineProps<{
    variant?: 'accent' | 'ghost' | 'dark'
    size?: 'md' | 'lg'
    to?: string
    href?: string
    type?: 'button' | 'submit'
    block?: boolean
    disabled?: boolean
    loading?: boolean
  }>(),
  { variant: 'accent', size: 'md', type: 'button' },
)

const tag = computed(() => (props.to ? RouterLink : props.href ? 'a' : 'button'))
const isInteractiveLink = computed(() => Boolean(props.to || props.href))

// Bind only the attribute that matches the rendered tag. Passing both `to` and
// an undefined `href` to RouterLink lets the undefined href fall through and
// clobber the href RouterLink computes, leaving the anchor with no href (not
// keyboard-navigable, no open-in-new-tab).
const linkBindings = computed(() => {
  if (props.to) return { to: props.to }
  if (props.href) return { href: props.href }
  return {}
})
</script>

<template>
  <component
    :is="tag"
    class="ui-btn"
    :class="[`ui-btn--${variant}`, `ui-btn--${size}`, { 'ui-btn--block': block }]"
    v-bind="linkBindings"
    :type="isInteractiveLink ? undefined : type"
    :disabled="!isInteractiveLink && (disabled || loading)"
    :aria-busy="loading || undefined"
  >
    <span v-if="loading" class="ui-btn__spinner" aria-hidden="true" />
    <slot />
  </component>
</template>

<style scoped>
.ui-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  border-radius: var(--radius-pill);
  font-weight: 600;
  text-align: center;
  transition:
    transform var(--dur-fast) var(--ease-out),
    background var(--dur-fast) ease,
    color var(--dur-fast) ease,
    box-shadow var(--dur-fast) ease,
    border-color var(--dur-fast) ease;
}
.ui-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}
.ui-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.ui-btn--md {
  padding: 0.7rem 1.2rem;
  font-size: var(--fs-body);
}
.ui-btn--lg {
  padding: 0.85rem 1.4rem;
  font-size: var(--fs-body-lg);
}
.ui-btn--block {
  display: flex;
  width: 100%;
}
.ui-btn--accent {
  background: var(--accent);
  color: var(--accent-ink);
}
.ui-btn--accent:hover:not(:disabled) {
  box-shadow: var(--shadow-accent);
}
.ui-btn--ghost {
  border: 1px solid var(--line-on-ink);
  color: var(--text-on-ink);
}
.ui-btn--ghost:hover:not(:disabled) {
  border-color: var(--text-on-ink);
}
.ui-btn--dark {
  background: var(--solid);
  color: var(--text-on-solid);
}
.ui-btn--dark:hover:not(:disabled) {
  background: var(--solid-2);
}
.ui-btn__spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid currentColor;
  border-top-color: transparent;
  animation: ui-btn-spin 0.7s linear infinite;
}
@keyframes ui-btn-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
