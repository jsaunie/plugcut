<script setup lang="ts">
defineProps<{ onPaper?: boolean }>()
</script>

<template>
  <div class="container">
    <div class="perforation" :class="{ 'perforation--on-paper': onPaper }" role="separator">
      <span class="perforation__scissors" aria-hidden="true">✂</span>
    </div>
  </div>
</template>
