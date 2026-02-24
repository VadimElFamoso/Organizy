<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Trash2, Check, Calendar } from 'lucide-vue-next'
import type { TaskItem } from '@/services/api'

defineProps<{
  task: TaskItem
}>()

const emit = defineEmits<{
  toggle: [id: string]
  delete: [id: string]
  openDetail: [task: TaskItem]
}>()

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}
</script>

<template>
  <div class="task-card" @click="emit('openDetail', task)">
    <div
      class="square"
      :class="{ filled: task.is_done }"
      @click.stop="emit('toggle', task.id)"
    >
      <Check v-if="task.is_done" :size="12" class="check-icon" />
    </div>
    <div class="card-body">
      <span class="card-title">{{ task.title }}</span>
      <span v-if="task.due_date" class="due-date">
        <Calendar :size="10" />
        {{ formatDate(task.due_date) }}
      </span>
    </div>
    <Button variant="ghost" size="sm" class="delete-btn" @click.stop="emit('delete', task.id)">
      <Trash2 :size="12" />
    </Button>
  </div>
</template>

<style scoped>
.task-card {
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

.task-card:hover {
  border-color: var(--app-border-hover);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.card-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.card-title {
  font-size: 0.82rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.due-date {
  font-size: 0.68rem;
  color: var(--app-text-dim);
  display: flex;
  align-items: center;
  gap: 3px;
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

.task-card:hover .delete-btn {
  opacity: 1;
}
</style>
