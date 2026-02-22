<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { useAuth } from '@/composables/useAuth'
import { useDailyTasks } from '@/composables/useDailyTasks'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import CompletionLineChart from '@/components/daily-tasks/CompletionLineChart.vue'
import CompletionTable from '@/components/daily-tasks/CompletionTable.vue'
import { Plus, Pencil, Trash2, Loader2 } from 'lucide-vue-next'
import type { DayStats } from '@/services/api'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const {
  tasks,
  completions,
  isLoading,
  fetchTasks,
  createTask,
  updateTask,
  deleteTask,
  toggleCompletion,
  fetchCompletions,
  getRangeStats,
} = useDailyTasks()

const showDialog = ref(false)
const editingId = ref<string | null>(null)
const taskName = ref('')
const taskDescription = ref('')
const rangeStats = ref<DayStats[]>([])

// Week dates for the table
const weekDates = computed(() => {
  const dates: string[] = []
  const today = new Date()
  // Show current week (Mon-Sun)
  const dayOfWeek = today.getDay()
  const monday = new Date(today)
  monday.setDate(today.getDate() - ((dayOfWeek + 6) % 7))
  for (let i = 0; i < 7; i++) {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    dates.push(d.toISOString().slice(0, 10))
  }
  return dates
})

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }
  await Promise.all([
    fetchTasks(),
    loadWeekCompletions(),
    loadRangeStats(),
  ])
})

async function loadWeekCompletions() {
  if (weekDates.value.length > 0) {
    await fetchCompletions(weekDates.value[0]!, weekDates.value[weekDates.value.length - 1]!)
  }
}

async function loadRangeStats() {
  const end = new Date()
  const start = new Date()
  start.setDate(end.getDate() - 30)
  const stats = await getRangeStats(
    start.toISOString().slice(0, 10),
    end.toISOString().slice(0, 10),
  )
  rangeStats.value = stats.days
}

function openCreate() {
  editingId.value = null
  taskName.value = ''
  taskDescription.value = ''
  showDialog.value = true
}

function openEdit(id: string) {
  const task = tasks.value.find(t => t.id === id)
  if (!task) return
  editingId.value = id
  taskName.value = task.name
  taskDescription.value = task.description || ''
  showDialog.value = true
}

async function saveTask() {
  if (!taskName.value.trim()) return
  if (editingId.value) {
    await updateTask(editingId.value, {
      name: taskName.value.trim(),
      description: taskDescription.value.trim() || null,
    })
  } else {
    await createTask(taskName.value.trim(), taskDescription.value.trim() || '')
  }
  showDialog.value = false
}

async function handleDelete(id: string) {
  await deleteTask(id)
}

async function handleToggle(taskId: string, date: string) {
  await toggleCompletion(taskId, date)
  await loadWeekCompletions()
}

const activeTasks = computed(() => tasks.value.filter(t => t.is_active))

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
        <h1>Daily Tasks</h1>
        <Button @click="openCreate" size="sm">
          <Plus :size="16" />
          Add Task
        </Button>
      </div>

      <div v-if="isLoading" class="loading">
        <Loader2 :size="32" class="spinner" />
      </div>

      <template v-else>
        <!-- Task List -->
        <section class="task-list-section">
          <div v-if="tasks.length === 0" class="empty-state">
            <p>No tasks yet. Create your first recurring task to start tracking.</p>
          </div>
          <div v-else class="task-list">
            <div v-for="task in tasks" :key="task.id" class="task-row" :class="{ inactive: !task.is_active }">
              <div class="task-info">
                <span class="task-name">{{ task.name }}</span>
                <span v-if="task.description" class="task-desc">{{ task.description }}</span>
                <span v-if="!task.is_active" class="inactive-badge">Inactive</span>
              </div>
              <div class="task-actions">
                <Button variant="ghost" size="sm" @click="openEdit(task.id)">
                  <Pencil :size="14" />
                </Button>
                <Button variant="ghost" size="sm" @click="handleDelete(task.id)">
                  <Trash2 :size="14" />
                </Button>
              </div>
            </div>
          </div>
        </section>

        <!-- Regularity View -->
        <section v-if="activeTasks.length > 0" class="regularity-section">
          <Tabs default-value="table">
            <TabsList>
              <TabsTrigger value="table">Week Table</TabsTrigger>
              <TabsTrigger value="graph">30-Day Graph</TabsTrigger>
            </TabsList>
            <TabsContent value="table">
              <CompletionTable
                :tasks="activeTasks"
                :completions="completions"
                :week-dates="weekDates"
                @toggle="handleToggle"
              />
            </TabsContent>
            <TabsContent value="graph">
              <CompletionLineChart :days="rangeStats" />
            </TabsContent>
          </Tabs>
        </section>
      </template>
    </main>

    <!-- Create/Edit Dialog -->
    <Dialog v-model:open="showDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ editingId ? 'Edit Task' : 'New Task' }}</DialogTitle>
          <DialogDescription>
            {{ editingId ? 'Update your recurring task.' : 'Add a recurring daily task to track.' }}
          </DialogDescription>
        </DialogHeader>
        <div class="dialog-form">
          <Input v-model="taskName" placeholder="Task name" @keyup.enter="saveTask" />
          <Input v-model="taskDescription" placeholder="Description (optional)" />
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showDialog = false">Cancel</Button>
          <Button @click="saveTask" :disabled="!taskName.trim()">
            {{ editingId ? 'Save' : 'Create' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--app-bg);
  color: var(--app-text);
}

.content {
  max-width: 900px;
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

.empty-state {
  text-align: center;
  padding: 48px;
  color: var(--app-text-muted);
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
}

.empty-state p {
  margin: 0;
}

.task-list-section {
  margin-bottom: 32px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  transition: border-color 0.15s;
}

.task-row:hover {
  border-color: var(--app-border-hover);
}

.task-row.inactive {
  opacity: 0.5;
}

.task-info {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.task-name {
  font-weight: 500;
  font-size: 0.9rem;
}

.task-desc {
  font-size: 0.8rem;
  color: var(--app-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inactive-badge {
  font-size: 0.7rem;
  padding: 2px 6px;
  background: var(--app-surface-3);
  border-radius: 4px;
  color: var(--app-text-muted);
}

.task-actions {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

.regularity-section {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 20px;
}

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 8px 0;
}

@media (max-width: 768px) {
  .content {
    padding: 24px 16px;
  }
}
</style>
