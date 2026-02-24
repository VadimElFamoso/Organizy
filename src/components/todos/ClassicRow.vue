<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
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

const priorityLabels: Record<string, string> = {
  urgent: 'Urgent',
  high: 'Haute',
  medium: 'Moyenne',
  low: 'Basse',
}

const priorityVariants: Record<string, string> = {
  urgent: 'destructive',
  high: 'default',
  medium: 'secondary',
  low: 'outline',
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}
</script>

<template>
  <div class="classic-row" @click="emit('openDetail', task)">
    <div
      class="square"
      :class="{ filled: task.is_done }"
      @click.stop="emit('toggle', task.id)"
    >
      <Check v-if="task.is_done" :size="12" class="check-icon" />
    </div>

    <span class="row-title">{{ task.title }}</span>

    <Badge
      v-if="task.priority"
      :variant="(priorityVariants[task.priority] as any) || 'secondary'"
      class="priority-badge"
    >
      {{ priorityLabels[task.priority] || task.priority }}
    </Badge>

    <span v-if="task.due_date" class="due-date">
      <Calendar :size="11" />
      {{ formatDate(task.due_date) }}
    </span>

    <Button variant="ghost" size="sm" class="delete-btn" @click.stop="emit('delete', task.id)">
      <Trash2 :size="13" />
    </Button>
  </div>
</template>

<style scoped>
.classic-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  transition: border-color 0.15s;
  cursor: pointer;
}

.classic-row:hover {
  border-color: var(--app-border-hover);
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

.row-title {
  font-size: 0.88rem;
  font-weight: 500;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.priority-badge {
  font-size: 0.62rem;
  text-transform: uppercase;
  flex-shrink: 0;
}

.due-date {
  font-size: 0.72rem;
  color: var(--app-text-dim);
  display: flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
}

.delete-btn {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
  padding: 4px;
  height: auto;
  color: var(--app-text-dim);
}

.classic-row:hover .delete-btn {
  opacity: 1;
}
</style>
