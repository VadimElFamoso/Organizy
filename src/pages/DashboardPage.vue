<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useSubscription } from '@/composables/useSubscription'
import { useDashboard } from '@/composables/useDashboard'
import { useDailyTasks } from '@/composables/useDailyTasks'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import TodayTasks from '@/components/dashboard/TodayTasks.vue'
import DotYearCalendar from '@/components/dashboard/DotYearCalendar.vue'
import WorkoutSummaryCard from '@/components/dashboard/WorkoutSummary.vue'
import TopTodos from '@/components/dashboard/TopTodos.vue'
import BudgetSummary from '@/components/dashboard/BudgetSummary.vue'
import { Loader2 } from 'lucide-vue-next'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const { isPro } = useSubscription(user)
const { dashboard, isLoading, fetchDashboard } = useDashboard()
const { toggleCompletion } = useDailyTasks()

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }
  await fetchDashboard()
})

async function handleToggleTask(taskId: string) {
  const d = new Date()
  const today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

  // Optimistic update for instant UI feedback
  if (dashboard.value) {
    const task = dashboard.value.today_tasks.find(t => t.task.id === taskId)
    if (task) task.completed = !task.completed
  }

  try {
    await toggleCompletion(taskId, today)
  } finally {
    await fetchDashboard()
  }
}

async function handleLogout() {
  await logout()
  router.push('/')
}
</script>

<template>
  <div class="dashboard-page">
    <AppNavbar mode="dashboard" :user="user" @logout="handleLogout" />

    <main class="content">
      <div v-if="isLoading" class="loading">
        <Loader2 :size="32" class="spinner" />
      </div>

      <template v-else-if="dashboard">
        <div class="page-header">
          <h1 class="page-title">Tableau de bord</h1>
          <span class="current-date">{{ new Date().toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</span>
        </div>

        <div class="dashboard-grid">
          <div class="left-column">
            <div class="year-column-card">
              <h3 class="year-title">Progression annuelle</h3>
              <DotYearCalendar :year="new Date().getFullYear()" />
            </div>
          </div>
          <div class="right-column">
            <TodayTasks
              :tasks="dashboard.today_tasks"
              class="cell-tasks"
              @toggle="handleToggleTask"
            />
            <WorkoutSummaryCard :summary="dashboard.workout_summary" class="cell-sport" />
            <TopTodos :todos="dashboard.top_todos" class="cell-kanban" />
            <BudgetSummary
              v-if="isPro && dashboard.budget_summary"
              :summary="dashboard.budget_summary"
              class="cell-budget"
            />
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: var(--app-bg);
  color: var(--app-text);
}

.content {
  max-width: 1300px;
  margin: 0 auto;
  padding: 32px 24px;
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

.page-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 28px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
}

.current-date {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--app-text);
}

.dashboard-grid {
  display: flex;
  gap: 24px;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
  flex-shrink: 0;
  width: 358px;
}

.year-column-card {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.year-title {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--app-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 0 0 14px;
  white-space: nowrap;
}

.right-column {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 24px;
  min-width: 0;
}

.cell-tasks {
  grid-column: 1;
  grid-row: 1;
}

.cell-kanban {
  grid-column: 1;
  grid-row: 2;
}

.cell-sport {
  grid-column: 2;
  grid-row: 1;
}

.cell-budget {
  grid-column: 2;
  grid-row: 2;
}

@media (max-width: 768px) {
  .dashboard-grid {
    flex-direction: column;
  }

  .left-column {
    width: 100%;
  }

  .year-column-card {
    flex-direction: row;
    overflow-x: auto;
    gap: 12px;
  }

  .right-column {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }

  .cell-tasks,
  .cell-kanban,
  .cell-sport,
  .cell-budget {
    grid-column: 1;
    grid-row: auto;
  }

  .content {
    padding: 24px 16px;
  }
}
</style>
