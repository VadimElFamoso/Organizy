<script setup lang="ts">
import KanbanColumn from './KanbanColumn.vue'
import type { TodoItem } from '@/services/api'

const props = defineProps<{
  todos: TodoItem[]
}>()

const emit = defineEmits<{
  add: [priority: string, title: string]
  toggle: [id: string]
  delete: [id: string]
  reorder: [items: { id: string; priority: string; sort_order: number }[]]
}>()

const columns = [
  { title: 'Urgent', priority: 'urgent' },
  { title: 'High', priority: 'high' },
  { title: 'Medium', priority: 'medium' },
  { title: 'Low', priority: 'low' },
]

function getColumnItems(priority: string): TodoItem[] {
  return props.todos
    .filter(t => t.priority === priority)
    .sort((a, b) => a.sort_order - b.sort_order)
}

function handleColumnUpdate(priority: string, items: TodoItem[]) {
  // Build reorder payload: all items in this column get the new priority and sort_order
  const reorderItems = items.map((item, index) => ({
    id: item.id,
    priority,
    sort_order: index,
  }))
  emit('reorder', reorderItems)
}
</script>

<template>
  <div class="kanban-board">
    <KanbanColumn
      v-for="col in columns"
      :key="col.priority"
      :title="col.title"
      :priority="col.priority"
      :items="getColumnItems(col.priority)"
      @update:items="handleColumnUpdate(col.priority, $event)"
      @add="(priority: string, title: string) => emit('add', priority, title)"
      @toggle="emit('toggle', $event)"
      @delete="emit('delete', $event)"
    />
  </div>
</template>

<style scoped>
.kanban-board {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  min-height: 300px;
}

@media (max-width: 1024px) {
  .kanban-board {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .kanban-board {
    grid-template-columns: 1fr;
  }
}
</style>
