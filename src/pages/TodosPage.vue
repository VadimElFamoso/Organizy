<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useTodos } from '@/composables/useTodos'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import KanbanBoard from '@/components/todos/KanbanBoard.vue'
import DoneArchive from '@/components/todos/DoneArchive.vue'
import { Loader2 } from 'lucide-vue-next'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const {
  todos,
  doneTodos,
  isLoading,
  fetchTodos,
  fetchDoneTodos,
  createTodo,
  updateTodo,
  deleteTodo,
  bulkDelete,
  reorder,
} = useTodos()

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }
  await Promise.all([fetchTodos(), fetchDoneTodos()])
})

async function handleAdd(priority: string, title: string) {
  await createTodo({ title, priority })
}

async function handleToggle(id: string) {
  await updateTodo(id, { is_done: true })
}

async function handleDelete(id: string) {
  await deleteTodo(id)
}

async function handleReorder(items: { id: string; priority: string; sort_order: number }[]) {
  await reorder(items)
}

async function handleBulkDelete(ids: string[]) {
  await bulkDelete(ids)
}

async function handleLogout() {
  await logout()
  router.push('/')
}
</script>

<template>
  <div class="page">
    <AppNavbar mode="dashboard" :user="user" @logout="handleLogout" />

    <main class="content">
      <div class="page-header">
        <h1>Todos</h1>
        <DoneArchive
          :todos="doneTodos"
          @bulk-delete="handleBulkDelete"
        />
      </div>

      <div v-if="isLoading" class="loading">
        <Loader2 :size="32" class="spinner" />
      </div>

      <template v-else>
        <KanbanBoard
          :todos="todos"
          @add="handleAdd"
          @toggle="handleToggle"
          @delete="handleDelete"
          @reorder="handleReorder"
        />
      </template>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--app-bg);
  color: var(--app-text);
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 64px;
}

.spinner {
  animation: spin 1s linear infinite;
  color: var(--app-text-muted);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .content {
    padding: 24px 16px;
  }
}
</style>
