<script setup lang="ts">
import { useRouter } from 'vue-router'
import { RouterLink } from 'vue-router'
import { ListTodo, Calendar, ArrowRight } from 'lucide-vue-next'
import type { DashboardTodoItem } from '@/services/api'

defineProps<{
  todos: DashboardTodoItem[]
}>()

const router = useRouter()

const priorityLabels: Record<string, string> = {
  urgent: 'Urgent',
  high: 'Haute',
  medium: 'Moyenne',
  low: 'Basse',
}

const priorityDotColors: Record<string, string> = {
  urgent: '#dc2626',
  high: '#ea580c',
  medium: '#78716c',
  low: '#a8a29e',
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

function isOverdue(dateStr: string): boolean {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const due = new Date(dateStr + 'T00:00:00')
  return due < today
}

function goToProject(projectId: string) {
  router.push(`/todos/${projectId}`)
}
</script>

<template>
  <div class="top-todos">
    <h3 class="section-title">
      <ListTodo :size="18" />
      Tâches prioritaires
    </h3>
    <div v-if="todos.length === 0" class="empty">
      <p>Aucune tâche active. Tout est en ordre !</p>
    </div>
    <template v-else>
      <div class="todo-list">
        <div
          v-for="todo in todos"
          :key="todo.id"
          class="todo-item"
          @click="goToProject(todo.project_id)"
        >
          <div
            class="priority-dot"
            :style="{ background: priorityDotColors[todo.priority || 'medium'] }"
            :title="priorityLabels[todo.priority || 'medium']"
          />
          <div class="todo-body">
            <span class="todo-title">{{ todo.title }}</span>
            <div class="todo-meta">
              <span class="todo-project">{{ todo.project_name }}</span>
              <span v-if="todo.due_date" class="todo-due" :class="{ overdue: isOverdue(todo.due_date) }">
                <Calendar :size="10" />
                {{ formatDate(todo.due_date) }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="footer">
        <RouterLink to="/todos" class="more-link">
          Voir tous les projets
          <ArrowRight :size="11" />
        </RouterLink>
      </div>
    </template>
  </div>
</template>

<style scoped>
.top-todos {
  background: var(--app-surface, #fff);
  border: 1px solid var(--app-border, #e2ddd5);
  border-radius: 12px;
  padding: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 0;
  color: var(--app-text-dim);
}

.empty {
  color: var(--app-text-muted);
  font-size: 0.875rem;
  text-align: center;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty p {
  margin: 0;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  justify-content: center;
  padding: 12px 0;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  min-width: 0;
}

.todo-item:hover {
  background: var(--app-surface-2);
}

.priority-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.todo-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.todo-title {
  font-size: 0.85rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.todo-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.68rem;
  color: var(--app-text-dim);
}

.todo-project {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.todo-due {
  display: flex;
  align-items: center;
  gap: 3px;
  white-space: nowrap;
  flex-shrink: 0;
}

.todo-due.overdue {
  color: #dc2626;
}

.footer {
  border-top: 1px solid var(--app-border);
  padding-top: 12px;
  margin-top: auto;
}

.more-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  font-weight: 500;
  color: var(--app-text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.more-link:hover {
  color: var(--app-text);
}
</style>
