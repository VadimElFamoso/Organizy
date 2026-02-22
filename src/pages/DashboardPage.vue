<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useDashboard } from '@/composables/useDashboard'
import { api } from '@/services/api'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import TodayTasks from '@/components/dashboard/TodayTasks.vue'
import DotYearCalendar from '@/components/dashboard/DotYearCalendar.vue'
import WorkoutSummaryCard from '@/components/dashboard/WorkoutSummary.vue'
import TopTodos from '@/components/dashboard/TopTodos.vue'
import { Loader2 } from 'lucide-vue-next'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const { dashboard, isLoading, fetchDashboard } = useDashboard()

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }
  await fetchDashboard()
})

async function handleToggleTask(taskId: string) {
  const today = new Date().toISOString().slice(0, 10)
  await api.toggleCompletion(taskId, today)
  await fetchDashboard()
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
          <h1 class="page-title">Dashboard</h1>
          <span class="current-date">{{ new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</span>
        </div>

        <div class="dashboard-grid">
          <div class="year-column-card">
            <h3 class="year-title">Year Progression</h3>
            <DotYearCalendar :year="new Date().getFullYear()" />
          </div>
          <div class="grid-main">
            <TodayTasks
              :tasks="dashboard.today_tasks"
              @toggle="handleToggleTask"
            />
            <div class="grid-row">
              <WorkoutSummaryCard :summary="dashboard.workout_summary" />
              <TopTodos :todos="dashboard.top_todos" />
            </div>
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
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.current-date {
  font-size: 0.9rem;
  color: var(--app-text-muted);
}

.dashboard-grid {
  display: flex;
  gap: 24px;
}

.year-column-card {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.year-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--app-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 12px;
  white-space: nowrap;
}

.grid-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-width: 0;
}

.grid-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 768px) {
  .dashboard-grid {
    flex-direction: column;
  }

  .year-column-card {
    flex-direction: row;
    overflow-x: auto;
    gap: 12px;
  }

  .grid-row {
    grid-template-columns: 1fr;
  }

  .content {
    padding: 24px 16px;
  }
}
</style>
