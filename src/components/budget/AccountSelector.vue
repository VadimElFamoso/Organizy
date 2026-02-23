<script setup lang="ts">
import type { BankAccount } from '@/services/api'

defineProps<{
  modelValue: string | null
  accounts: BankAccount[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
}>()
</script>

<template>
  <select
    class="account-select"
    :value="modelValue || ''"
    @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value || null)"
  >
    <option value="">Tous les comptes</option>
    <option
      v-for="acc in accounts"
      :key="acc.id"
      :value="acc.id"
    >
      {{ acc.name }}
    </option>
  </select>
</template>

<style scoped>
.account-select {
  padding: 6px 12px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  font-size: 0.85rem;
  color: var(--app-text);
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s;
}

.account-select:focus {
  border-color: var(--app-text);
}
</style>
