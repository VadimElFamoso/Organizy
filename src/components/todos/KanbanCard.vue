<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Trash2, Check } from 'lucide-vue-next'
import type { TodoItem } from '@/services/api'

defineProps<{
  todo: TodoItem
}>()

const emit = defineEmits<{
  toggle: [id: string]
  delete: [id: string]
}>()
</script>

<template>
  <div class="kanban-card">
    <div
      class="square"
      :class="{ filled: todo.is_done }"
      @click.stop="emit('toggle', todo.id)"
    >
      <Check v-if="todo.is_done" :size="12" class="check-icon" />
    </div>
    <span class="card-title">{{ todo.title }}</span>
    <Button variant="ghost" size="sm" class="delete-btn" @click="emit('delete', todo.id)">
      <Trash2 :size="12" />
    </Button>
  </div>
</template>

<style scoped>
.kanban-card {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--app-surface, #fff);
  border: 1px solid var(--app-border, #e2ddd5);
  border-radius: 8px;
  padding: 8px 10px;
  cursor: grab;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.kanban-card:hover {
  border-color: var(--app-border-hover);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.card-title {
  font-size: 0.82rem;
  font-weight: 500;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.square {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.square.filled {
  background: var(--app-text);
  border-color: var(--app-text);
}

.check-icon {
  color: var(--app-surface);
}

.square:hover:not(.filled) {
  border-color: var(--app-border-hover);
  background: var(--app-surface-3);
}

.delete-btn {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
  padding: 4px;
  height: auto;
}

.kanban-card:hover .delete-btn {
  opacity: 1;
}
</style>
