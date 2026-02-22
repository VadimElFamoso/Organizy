<script setup lang="ts">
import { ListTodo } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import type { TodoItem } from '@/services/api'

defineProps<{
  todos: TodoItem[]
}>()

const priorityColors: Record<string, string> = {
  urgent: 'destructive',
  high: 'default',
  medium: 'secondary',
  low: 'outline',
}
</script>

<template>
  <div class="top-todos">
    <h3 class="section-title">
      <ListTodo :size="18" />
      Top Todos
    </h3>
    <div v-if="todos.length === 0" class="empty">
      <p>No active todos. All clear!</p>
    </div>
    <div v-else class="todo-list">
      <div v-for="todo in todos" :key="todo.id" class="todo-item">
        <Badge :variant="(priorityColors[todo.priority] as any) || 'secondary'" class="priority-badge">
          {{ todo.priority }}
        </Badge>
        <span class="todo-title">{{ todo.title }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.top-todos {
  background: var(--app-surface, #fff);
  border: 1px solid var(--app-border, #e2ddd5);
  border-radius: 12px;
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 16px;
  color: var(--app-text);
}

.section-title svg {
  color: var(--theme-accent);
}

.empty {
  color: var(--app-text-muted);
  font-size: 0.875rem;
  text-align: center;
  padding: 16px 0;
}

.empty p {
  margin: 0;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.15s;
}

.todo-item:hover {
  background: var(--app-surface-2);
}

.priority-badge {
  font-size: 0.65rem;
  text-transform: uppercase;
  flex-shrink: 0;
}

.todo-title {
  font-size: 0.9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
