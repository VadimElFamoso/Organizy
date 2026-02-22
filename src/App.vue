<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import ToastContainer from '@/components/ui/ToastContainer.vue'

const { init: initAuth } = useAuth()

onMounted(async () => {
  await initAuth()
})
</script>

<template>
  <RouterView />
  <ToastContainer />
</template>

<style>
:root {
  --app-bg: #0a0a0b;
  --app-surface: #111113;
  --app-surface-2: #18181b;
  --app-surface-3: #27272a;
  --app-border: #27272a;
  --app-border-hover: #3f3f46;
  --app-text: #fafafa;
  --app-text-muted: #a1a1aa;
  --app-text-dim: #71717a;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--app-bg);
  color: var(--app-text);
}
</style>
