<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { useAuth } from '@/composables/useAuth'
import { useWorkouts } from '@/composables/useWorkouts'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import WorkoutCalendar from '@/components/workouts/WorkoutCalendar.vue'
import WorkoutHistory from '@/components/workouts/WorkoutHistory.vue'
import { Plus, Loader2, Dumbbell, Flame } from 'lucide-vue-next'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const {
  workouts,
  summary,
  calendarDays,
  workoutTypes,
  isLoading,
  fetchWorkouts,
  createWorkout,
  updateWorkout,
  deleteWorkout,
  fetchSummary,
  fetchCalendar,
  fetchWorkoutTypes,
} = useWorkouts()

const showDialog = ref(false)
const editingId = ref<string | null>(null)
const formType = ref('')
const formNotes = ref('')
const formDate = ref(new Date().toISOString().slice(0, 10))
const formDuration = ref<string>('')
const showSuggestions = ref(false)

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }
  await Promise.all([
    fetchWorkouts(),
    fetchSummary(),
    fetchWorkoutTypes(),
  ])
})

function openCreate() {
  editingId.value = null
  formType.value = ''
  formNotes.value = ''
  formDate.value = new Date().toISOString().slice(0, 10)
  formDuration.value = ''
  showDialog.value = true
}

function openEdit(id: string) {
  const w = workouts.value.find(w => w.id === id)
  if (!w) return
  editingId.value = id
  formType.value = w.workout_type
  formNotes.value = w.notes || ''
  formDate.value = w.workout_date
  formDuration.value = w.duration_minutes?.toString() || ''
  showDialog.value = true
}

async function saveWorkout() {
  if (!formType.value.trim() || !formDate.value) return
  const data = {
    workout_type: formType.value.trim(),
    notes: formNotes.value.trim() || undefined,
    workout_date: formDate.value,
    duration_minutes: formDuration.value ? parseInt(formDuration.value) : undefined,
  }

  if (editingId.value) {
    await updateWorkout(editingId.value, data)
  } else {
    await createWorkout(data)
  }
  showDialog.value = false
  // Refresh calendar for the current month view
  const d = new Date(formDate.value)
  await fetchCalendar(d.getFullYear(), d.getMonth() + 1)
}

async function handleDelete(id: string) {
  await deleteWorkout(id)
}

function handleMonthChange(year: number, month: number) {
  fetchCalendar(year, month)
}

function selectSuggestion(type: string) {
  formType.value = type
  showSuggestions.value = false
}

function hideSuggestions() {
  window.setTimeout(() => { showSuggestions.value = false }, 200)
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
        <h1>Workouts</h1>
        <Button @click="openCreate" size="sm">
          <Plus :size="16" />
          Log Workout
        </Button>
      </div>

      <div v-if="isLoading" class="loading">
        <Loader2 :size="32" class="spinner" />
      </div>

      <template v-else>
        <!-- Summary stats row -->
        <div v-if="summary" class="summary-row">
          <div class="summary-stat">
            <Dumbbell :size="18" class="stat-icon" />
            <div>
              <span class="stat-value">{{ summary.total_workouts }}</span>
              <span class="stat-label">Total workouts</span>
            </div>
          </div>
          <div class="summary-stat">
            <Flame :size="18" class="stat-icon" />
            <div>
              <span class="stat-value">{{ summary.current_streak }}</span>
              <span class="stat-label">Day streak</span>
            </div>
          </div>
        </div>

        <div class="workout-grid">
          <WorkoutCalendar
            :days="calendarDays"
            @month-change="handleMonthChange"
          />
          <WorkoutHistory
            :workouts="workouts"
            @edit="openEdit"
            @delete="handleDelete"
          />
        </div>
      </template>
    </main>

    <!-- Create/Edit Dialog -->
    <Dialog v-model:open="showDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ editingId ? 'Edit Workout' : 'Log Workout' }}</DialogTitle>
          <DialogDescription>
            {{ editingId ? 'Update workout details.' : 'Record a workout session.' }}
          </DialogDescription>
        </DialogHeader>
        <div class="dialog-form">
          <div class="form-field">
            <label>Type</label>
            <div class="type-input-wrapper">
              <Input
                v-model="formType"
                placeholder="e.g., Running, Weight Training"
                @focus="showSuggestions = true"
                @blur="hideSuggestions"
              />
              <div v-if="showSuggestions && workoutTypes.length > 0" class="suggestions">
                <button
                  v-for="t in workoutTypes.filter(t => t.toLowerCase().includes(formType.toLowerCase()))"
                  :key="t"
                  class="suggestion"
                  @mousedown="selectSuggestion(t)"
                >
                  {{ t }}
                </button>
              </div>
            </div>
          </div>
          <div class="form-field">
            <label>Date</label>
            <Input v-model="formDate" type="date" />
          </div>
          <div class="form-field">
            <label>Duration (minutes)</label>
            <Input v-model="formDuration" type="number" placeholder="Optional" />
          </div>
          <div class="form-field">
            <label>Notes</label>
            <Input v-model="formNotes" placeholder="Optional notes" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showDialog = false">Cancel</Button>
          <Button @click="saveWorkout" :disabled="!formType.trim() || !formDate">
            {{ editingId ? 'Save' : 'Log' }}
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
  max-width: 1000px;
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

.summary-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.summary-stat {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  flex: 1;
}

.stat-icon {
  color: var(--theme-accent);
}

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: var(--app-text-muted);
}

.workout-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 8px 0;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-field label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--app-text-muted);
}

.type-input-wrapper {
  position: relative;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  margin-top: 4px;
  z-index: 10;
  max-height: 150px;
  overflow-y: auto;
}

.suggestion {
  display: block;
  width: 100%;
  text-align: left;
  padding: 8px 12px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--app-text);
}

.suggestion:hover {
  background: var(--app-surface-2);
}

@media (max-width: 768px) {
  .workout-grid {
    grid-template-columns: 1fr;
  }

  .summary-row {
    flex-direction: column;
  }

  .content {
    padding: 24px 16px;
  }
}
</style>
