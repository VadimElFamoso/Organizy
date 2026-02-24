<script setup lang="ts">
import { Check } from 'lucide-vue-next'

defineProps<{
  modelValue?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [color: string]
}>()

const presetColors = [
  '#dc2626', '#ea580c', '#f59e0b', '#16a34a', '#0ea5e9',
  '#6366f1', '#a855f7', '#ec4899', '#78716c', '#a8a29e',
]
</script>

<template>
  <div class="color-picker">
    <button
      v-for="color in presetColors"
      :key="color"
      class="swatch"
      :class="{ active: modelValue === color }"
      :style="{ background: color }"
      @click="emit('update:modelValue', color)"
    >
      <Check v-if="modelValue === color" :size="10" class="check" />
    </button>
  </div>
</template>

<style scoped>
.color-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.swatch {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.swatch:hover {
  transform: scale(1.15);
}

.swatch.active {
  border-color: var(--app-text);
  box-shadow: 0 0 0 2px var(--app-surface), 0 0 0 4px var(--app-text);
}

.check {
  color: #fff;
}
</style>
