<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
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
import { Plus, Pencil, Trash2, Loader2, ChevronLeft, ChevronRight } from 'lucide-vue-next'
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

function toLocalDate(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const today = computed(() => toLocalDate(new Date()))

// Week navigation (table view)
const weekOffset = ref(0)

const weekDates = computed(() => {
  const now = new Date()
  const dayOfWeek = now.getDay()
  const monday = new Date(now)
  monday.setDate(now.getDate() - ((dayOfWeek + 6) % 7) + (weekOffset.value * 7))
  const dates: string[] = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    dates.push(toLocalDate(d))
  }
  return dates
})

const weekLabel = computed(() => {
  if (weekDates.value.length === 0) return ''
  const start = new Date(weekDates.value[0]!)
  const end = new Date(weekDates.value[weekDates.value.length - 1]!)
  const fmt = (d: Date) => d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
  const yearStr = end.getFullYear()
  return `${fmt(start)} — ${fmt(end)} ${yearStr}`
})

function prevWeek() {
  weekOffset.value--
}

function nextWeek() {
  if (weekOffset.value < 0) weekOffset.value++
}

watch(weekOffset, () => {
  loadWeekCompletions()
})

// Graph period navigation
type GraphPeriod = 'week' | 'month' | 'year'
const graphPeriod = ref<GraphPeriod>('month')
const graphOffset = ref(0)

const graphRange = computed(() => {
  const now = new Date()
  let start: Date
  let end: Date

  if (graphPeriod.value === 'week') {
    const dayOfWeek = now.getDay()
    const monday = new Date(now)
    monday.setDate(now.getDate() - ((dayOfWeek + 6) % 7) + (graphOffset.value * 7))
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)
    start = monday
    end = sunday
  } else if (graphPeriod.value === 'month') {
    const base = new Date(now.getFullYear(), now.getMonth() + graphOffset.value, 1)
    start = base
    end = new Date(base.getFullYear(), base.getMonth() + 1, 0)
  } else {
    const year = now.getFullYear() + graphOffset.value
    start = new Date(year, 0, 1)
    end = new Date(year, 11, 31)
  }

  // Cap end at today
  const todayDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  if (end > todayDate) end = todayDate

  return { start, end }
})

const graphLabel = computed(() => {
  const { start, end } = graphRange.value
  const fmt = (d: Date) => d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })

  if (graphPeriod.value === 'year') {
    return `${start.getFullYear()}`
  }
  if (graphPeriod.value === 'month') {
    return start.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
  }
  return `${fmt(start)} — ${fmt(end)} ${end.getFullYear()}`
})

function setGraphPeriod(period: GraphPeriod) {
  graphPeriod.value = period
  graphOffset.value = 0
}

function prevGraph() {
  graphOffset.value--
}

function nextGraph() {
  if (graphOffset.value < 0) graphOffset.value++
}

watch([graphPeriod, graphOffset], () => {
  loadRangeStats()
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
  const { start, end } = graphRange.value
  const stats = await getRangeStats(
    toLocalDate(start),
    toLocalDate(end),
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
        <h1>Tâches quotidiennes</h1>
        <Button @click="openCreate" size="sm">
          <Plus :size="16" />
          Ajouter
        </Button>
      </div>

      <div v-if="isLoading" class="loading">
        <Loader2 :size="32" class="spinner" />
      </div>

      <template v-else>
        <!-- Task List -->
        <section class="task-list-section">
          <div v-if="tasks.length === 0" class="empty-state">
            <p>Aucune tâche pour le moment. Créez votre première tâche récurrente.</p>
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
              <TabsTrigger value="table">Semaine</TabsTrigger>
              <TabsTrigger value="graph">Graphiques</TabsTrigger>
            </TabsList>
            <TabsContent value="table">
              <div class="period-nav">
                <Button variant="ghost" size="sm" @click="prevWeek">
                  <ChevronLeft :size="16" />
                </Button>
                <span class="period-label">{{ weekLabel }}</span>
                <Button variant="ghost" size="sm" @click="nextWeek" :disabled="weekOffset >= 0">
                  <ChevronRight :size="16" />
                </Button>
              </div>
              <CompletionTable
                :tasks="activeTasks"
                :completions="completions"
                :week-dates="weekDates"
                :today="today"
                @toggle="handleToggle"
              />
            </TabsContent>
            <TabsContent value="graph">
              <div class="graph-controls">
                <div class="period-switcher">
                  <button
                    class="period-btn"
                    :class="{ active: graphPeriod === 'week' }"
                    @click="setGraphPeriod('week')"
                  >Semaine</button>
                  <button
                    class="period-btn"
                    :class="{ active: graphPeriod === 'month' }"
                    @click="setGraphPeriod('month')"
                  >Mois</button>
                  <button
                    class="period-btn"
                    :class="{ active: graphPeriod === 'year' }"
                    @click="setGraphPeriod('year')"
                  >Année</button>
                </div>
                <div class="period-nav">
                  <Button variant="ghost" size="sm" @click="prevGraph">
                    <ChevronLeft :size="16" />
                  </Button>
                  <span class="period-label">{{ graphLabel }}</span>
                  <Button variant="ghost" size="sm" @click="nextGraph" :disabled="graphOffset >= 0">
                    <ChevronRight :size="16" />
                  </Button>
                </div>
              </div>
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
          <DialogTitle>{{ editingId ? 'Modifier la tâche' : 'Nouvelle tâche' }}</DialogTitle>
          <DialogDescription>
            {{ editingId ? 'Modifiez votre tâche récurrente.' : 'Ajoutez une tâche quotidienne récurrente à suivre.' }}
          </DialogDescription>
        </DialogHeader>
        <div class="dialog-form">
          <Input v-model="taskName" placeholder="Nom de la tâche" @keyup.enter="saveTask" />
          <Input v-model="taskDescription" placeholder="Description (facultatif)" />
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showDialog = false">Annuler</Button>
          <Button @click="saveTask" :disabled="!taskName.trim()">
            {{ editingId ? 'Enregistrer' : 'Créer' }}
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
  margin-bottom: 28px;
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
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
  font-size: 0.9rem;
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
  padding: 14px 16px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 10px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.task-row:hover {
  border-color: var(--app-border-hover);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
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
  font-size: 0.88rem;
}

.task-desc {
  font-size: 0.8rem;
  color: var(--app-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inactive-badge {
  font-size: 0.65rem;
  padding: 2px 8px;
  background: var(--app-surface-3);
  border-radius: 4px;
  color: var(--app-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-weight: 600;
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
  padding: 20px 20px 20px 16px;
}

.graph-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.period-switcher {
  display: flex;
  gap: 2px;
  background: var(--app-surface-2);
  border-radius: 8px;
  padding: 3px;
}

.period-btn {
  padding: 5px 14px;
  font-size: 0.78rem;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--app-text-muted);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.period-btn:hover {
  color: var(--app-text);
}

.period-btn.active {
  background: var(--app-surface);
  color: var(--app-text);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.period-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.period-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--app-text-muted);
  min-width: 180px;
  text-align: center;
  text-transform: capitalize;
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
