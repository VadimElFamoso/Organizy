<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useProjectBoard } from '@/composables/useProjectBoard'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import KanbanView from '@/components/todos/KanbanView.vue'
import EisenhowerView from '@/components/todos/EisenhowerView.vue'
import ClassicView from '@/components/todos/ClassicView.vue'
import DoneArchive from '@/components/todos/DoneArchive.vue'
import CreateTaskDialog from '@/components/todos/CreateTaskDialog.vue'
import TaskDetailSheet from '@/components/todos/TaskDetailSheet.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2, ArrowLeft, Pencil } from 'lucide-vue-next'
import type { TaskItem } from '@/services/api'

const route = useRoute()
const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()

const projectId = route.params.id as string
const {
  project,
  columns,
  items,
  doneItems,
  itemsByColumn,
  isLoading,
  fetchProject,
  updateProjectName,
  addColumn,
  updateColumn,
  deleteColumn,
  reorderColumns,
  createTask,
  updateTask,
  deleteTask,
  bulkDeleteTasks,
  reorderTasks,
} = useProjectBoard(projectId)

const isEditing = ref(false)
const editName = ref('')

// Task detail sheet
const selectedTask = ref<TaskItem | null>(null)
const detailOpen = ref(false)

function startEdit() {
  editName.value = project.value?.name || ''
  isEditing.value = true
}

async function saveName() {
  if (editName.value.trim() && editName.value.trim() !== project.value?.name) {
    await updateProjectName(editName.value.trim())
  }
  isEditing.value = false
}

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }
  await fetchProject()
})

async function handleCreateTask(data: { title: string; description?: string; column_id?: string; priority?: string; due_date?: string }) {
  await createTask(data)
}

async function handleToggle(id: string) {
  const task = items.value.find(t => t.id === id)
  if (task) {
    await updateTask(id, { is_done: true })
  } else {
    // Was done, undo
    await updateTask(id, { is_done: false })
  }
}

async function handleDelete(id: string) {
  await deleteTask(id)
}

async function handleBulkDelete(ids: string[]) {
  await bulkDeleteTasks(ids)
}

async function handleReorder(reorderItems: { id: string; column_id?: string | null; sort_order: number }[]) {
  await reorderTasks(reorderItems)
}

async function handleReorderColumns(colItems: { id: string; sort_order: number }[]) {
  await reorderColumns(colItems)
}

async function handleRecover(id: string) {
  await updateTask(id, { is_done: false })
}

function handleOpenDetail(task: TaskItem) {
  selectedTask.value = task
  detailOpen.value = true
}

async function handleDetailSave(id: string, data: Partial<{ title: string; description: string | null; column_id: string | null; priority: string | null; due_date: string | null }>) {
  await updateTask(id, data)
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
        <div class="header-left">
          <Button variant="ghost" size="sm" @click="router.push('/todos')">
            <ArrowLeft :size="16" />
          </Button>

          <template v-if="isEditing">
            <Input
              v-model="editName"
              class="name-input"
              @keyup.enter="saveName"
              @keyup.escape="isEditing = false"
              @blur="saveName"
            />
          </template>
          <template v-else>
            <h1 @click="startEdit">
              {{ project?.name || '...' }}
              <Pencil :size="14" class="edit-icon" />
            </h1>
          </template>
        </div>

        <div class="header-right">
          <CreateTaskDialog
            v-if="project"
            :method="project.method"
            :columns="columns"
            @create="handleCreateTask"
          />
          <DoneArchive
            :todos="doneItems"
            @bulk-delete="handleBulkDelete"
            @delete="handleDelete"
            @recover="handleRecover"
          />
        </div>
      </div>

      <div v-if="isLoading" class="loading">
        <Loader2 :size="32" class="spinner" />
      </div>

      <template v-else-if="project">
        <KanbanView
          v-if="project.method === 'kanban'"
          :project-id="projectId"
          :columns="columns"
          :items-by-column="itemsByColumn"
          @toggle="handleToggle"
          @delete="handleDelete"
          @reorder="handleReorder"
          @add-column="addColumn"
          @update-column="updateColumn"
          @delete-column="deleteColumn"
          @reorder-columns="handleReorderColumns"
          @open-detail="handleOpenDetail"
        />

        <EisenhowerView
          v-else-if="project.method === 'eisenhower'"
          :columns="columns"
          :items-by-column="itemsByColumn"
          @toggle="handleToggle"
          @delete="handleDelete"
          @reorder="handleReorder"
          @update-column="updateColumn"
          @open-detail="handleOpenDetail"
        />

        <ClassicView
          v-else-if="project.method === 'classic'"
          :items="items"
          @toggle="handleToggle"
          @delete="handleDelete"
          @open-detail="handleOpenDetail"
        />

        <TaskDetailSheet
          :task="selectedTask"
          :open="detailOpen"
          :method="project.method"
          :columns="columns"
          @update:open="detailOpen = $event"
          @save="handleDetailSave"
          @delete="handleDelete"
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
  max-width: 1300px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.header-left h1 {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.edit-icon {
  color: var(--app-text-dim);
  opacity: 0;
  transition: opacity 0.15s;
}

.header-left h1:hover .edit-icon {
  opacity: 1;
}

.name-input {
  font-size: 1.25rem;
  font-weight: 600;
  max-width: 300px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
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
    padding: 24px 16px 88px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .name-input {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .content {
    padding: 16px 12px 88px;
  }

  .page-header {
    gap: 10px;
    margin-bottom: 20px;
  }

  .header-left h1 {
    font-size: 1.35rem;
  }
}
</style>
