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
import { Plus, Loader2, Dumbbell, Flame, X, ChevronDown, Bookmark, Trash2, Pencil, ArrowRight } from 'lucide-vue-next'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const {
  workouts,
  summary,
  calendarDays,
  workoutTypes,
  selectedDateWorkouts,
  presets,
  isLoading,
  fetchWorkouts,
  createWorkout,
  updateWorkout,
  deleteWorkout,
  fetchSummary,
  fetchCalendar,
  fetchWorkoutTypes,
  fetchWorkoutsByDate,
  fetchPresets,
  createPreset,
  updatePreset,
  deletePreset,
} = useWorkouts()

const showDialog = ref(false)
const editingId = ref<string | null>(null)
const formType = ref('')
const formNotes = ref('')
const formDuration = ref<string>('')
const formExercises = ref<{ name: string; notes: string }[]>([])
const showSuggestions = ref(false)
const selectedDate = ref<string | null>(null)
const expandedDayWorkout = ref<string | null>(null)
const showPresetDropdown = ref(false)
const saveAsPreset = ref(false)
const presetName = ref('')

// Preset edit dialog
const showPresetDialog = ref(false)
const editingPresetId = ref<string | null>(null)
const presetFormName = ref('')
const presetFormType = ref('')
const presetFormDuration = ref<string>('')
const presetFormExercises = ref<{ name: string; notes: string }[]>([])

function toggleDaySession(id: string) {
  expandedDayWorkout.value = expandedDayWorkout.value === id ? null : id
}

function todayStr() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }
  await Promise.all([
    fetchWorkouts(),
    fetchSummary(),
    fetchWorkoutTypes(),
    fetchPresets(),
  ])
  // Auto-select today
  selectedDate.value = todayStr()
  await fetchWorkoutsByDate(selectedDate.value)
})

function openCreate() {
  editingId.value = null
  formType.value = ''
  formNotes.value = ''
  formDuration.value = ''
  formExercises.value = []
  saveAsPreset.value = false
  presetName.value = ''
  showPresetDropdown.value = false
  showDialog.value = true
}

function openEdit(id: string) {
  const w = workouts.value.find(w => w.id === id)
  if (!w) return
  editingId.value = id
  formType.value = w.workout_type
  formNotes.value = w.notes || ''
  formDuration.value = w.duration_minutes?.toString() || ''
  formExercises.value = w.exercises.map(ex => ({ name: ex.name, notes: ex.notes || '' }))
  saveAsPreset.value = false
  presetName.value = ''
  showPresetDropdown.value = false
  showDialog.value = true
}

function addExercise() {
  formExercises.value.push({ name: '', notes: '' })
}

function removeExercise(index: number) {
  formExercises.value.splice(index, 1)
}

function loadPreset(presetId: string) {
  const preset = presets.value.find(p => p.id === presetId)
  if (!preset) return
  formType.value = preset.workout_type
  formDuration.value = preset.duration_minutes?.toString() || ''
  formExercises.value = preset.exercises.map(ex => ({ name: ex.name, notes: ex.notes || '' }))
  showPresetDropdown.value = false
}

async function handleDeletePreset(presetId: string) {
  await deletePreset(presetId)
}

function openCreatePreset() {
  editingPresetId.value = null
  presetFormName.value = ''
  presetFormType.value = ''
  presetFormDuration.value = ''
  presetFormExercises.value = []
  showPresetDialog.value = true
}

function openEditPreset(presetId: string) {
  const preset = presets.value.find(p => p.id === presetId)
  if (!preset) return
  editingPresetId.value = presetId
  presetFormName.value = preset.name
  presetFormType.value = preset.workout_type
  presetFormDuration.value = preset.duration_minutes?.toString() || ''
  presetFormExercises.value = preset.exercises.map(ex => ({ name: ex.name, notes: ex.notes || '' }))
  showPresetDialog.value = true
}

function addPresetExercise() {
  presetFormExercises.value.push({ name: '', notes: '' })
}

function removePresetExercise(index: number) {
  presetFormExercises.value.splice(index, 1)
}

async function savePresetForm() {
  if (!presetFormName.value.trim() || !presetFormType.value.trim()) return
  const exercises = presetFormExercises.value
    .filter(ex => ex.name.trim())
    .map((ex, i) => ({
      name: ex.name.trim(),
      notes: ex.notes.trim() || undefined,
      sort_order: i,
    }))
  if (editingPresetId.value) {
    await updatePreset(editingPresetId.value, {
      name: presetFormName.value.trim(),
      workout_type: presetFormType.value.trim(),
      duration_minutes: presetFormDuration.value ? parseInt(presetFormDuration.value) : null,
      exercises,
    })
  } else {
    await createPreset({
      name: presetFormName.value.trim(),
      workout_type: presetFormType.value.trim(),
      duration_minutes: presetFormDuration.value ? parseInt(presetFormDuration.value) : undefined,
      exercises,
    })
  }
  showPresetDialog.value = false
}

async function saveWorkout() {
  if (!formType.value.trim()) return
  const exercises = formExercises.value
    .filter(ex => ex.name.trim())
    .map((ex, i) => ({
      name: ex.name.trim(),
      notes: ex.notes.trim() || undefined,
      sort_order: i,
    }))

  if (editingId.value) {
    await updateWorkout(editingId.value, {
      workout_type: formType.value.trim(),
      notes: formNotes.value.trim() || null,
      duration_minutes: formDuration.value ? parseInt(formDuration.value) : null,
      exercises,
    })
  } else {
    await createWorkout({
      workout_type: formType.value.trim(),
      notes: formNotes.value.trim() || undefined,
      duration_minutes: formDuration.value ? parseInt(formDuration.value) : undefined,
      exercises,
    })
  }

  // Save as preset if requested
  if (saveAsPreset.value && presetName.value.trim()) {
    await createPreset({
      name: presetName.value.trim(),
      workout_type: formType.value.trim(),
      duration_minutes: formDuration.value ? parseInt(formDuration.value) : undefined,
      exercises,
    })
  }

  showDialog.value = false
  // Refresh calendar for the current month view
  const now = new Date()
  await fetchCalendar(now.getFullYear(), now.getMonth() + 1)
  // Refresh selected date if viewing one
  if (selectedDate.value) {
    await fetchWorkoutsByDate(selectedDate.value)
  }
}

async function handleDelete(id: string) {
  await deleteWorkout(id)
  const now = new Date()
  await fetchCalendar(now.getFullYear(), now.getMonth() + 1)
  if (selectedDate.value) {
    await fetchWorkoutsByDate(selectedDate.value)
  }
}

function handleMonthChange(year: number, month: number) {
  fetchCalendar(year, month)
}

async function handleDayClick(dateStr: string) {
  selectedDate.value = dateStr
  await fetchWorkoutsByDate(dateStr)
}

function selectSuggestion(type: string) {
  formType.value = type
  showSuggestions.value = false
}

function hideSuggestions() {
  window.setTimeout(() => { showSuggestions.value = false }, 200)
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })
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
        <h1>Sport</h1>
        <Button @click="openCreate" size="sm">
          <Plus :size="16" />
          Ajouter
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
              <span class="stat-label">Total séances</span>
            </div>
          </div>
          <div class="summary-stat">
            <Flame :size="18" class="stat-icon" />
            <div>
              <span class="stat-value">{{ summary.current_streak }}</span>
              <span class="stat-label">Jours consécutifs</span>
            </div>
          </div>
        </div>

        <div class="workout-grid">
          <div class="calendar-column">
            <WorkoutCalendar
              :days="calendarDays"
              :min-date="user?.created_at"
              @month-change="handleMonthChange"
              @day-click="handleDayClick"
            />
            <!-- Selected date detail (today by default) -->
            <div class="date-detail">
              <h3 class="date-detail-title">{{ selectedDate ? formatDate(selectedDate) : "Aujourd'hui" }}</h3>
              <div v-if="selectedDateWorkouts.length === 0" class="date-detail-empty">
                Aucune séance ce jour.
              </div>
              <div v-else class="date-detail-list">
                <div v-for="w in selectedDateWorkouts" :key="w.id" class="date-session" :class="{ expanded: expandedDayWorkout === w.id }">
                  <div class="date-session-header" @click="toggleDaySession(w.id)">
                    <span class="date-session-type">{{ w.workout_type }}</span>
                    <div class="date-session-right">
                      <span v-if="w.duration_minutes" class="date-session-duration">{{ w.duration_minutes }}m</span>
                      <ChevronDown :size="14" class="date-session-chevron" :class="{ rotated: expandedDayWorkout === w.id }" />
                    </div>
                  </div>
                  <div v-if="expandedDayWorkout === w.id" class="date-session-body">
                    <p v-if="w.notes" class="date-session-notes">{{ w.notes }}</p>
                    <div v-if="w.exercises.length > 0" class="date-session-exercises">
                      <div v-for="ex in w.exercises" :key="ex.id || ex.sort_order" class="date-exercise">
                        <span class="date-exercise-name">{{ ex.name }}</span>
                        <span v-if="ex.notes" class="date-exercise-notes">{{ ex.notes }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="right-column">
            <!-- Séances récentes -->
            <div class="history-panel">
              <h3 class="panel-title">Séances récentes</h3>
              <div class="history-scroll">
                <WorkoutHistory
                  :workouts="workouts"
                  @edit="openEdit"
                  @delete="handleDelete"
                />
              </div>
            </div>

            <!-- Presets panel -->
            <div class="presets-panel">
              <div class="panel-title-row">
                <h3 class="panel-title">
                  <Bookmark :size="14" />
                  Presets
                </h3>
                <Button variant="ghost" size="sm" @click="openCreatePreset">
                  <Plus :size="14" />
                </Button>
              </div>
              <div v-if="presets.length === 0" class="presets-panel-empty">
                Aucun preset.
              </div>
              <div v-else class="presets-panel-scroll">
                <div v-for="p in presets" :key="p.id" class="presets-panel-item">
                  <div class="presets-panel-info">
                    <span class="presets-panel-name">{{ p.name }}</span>
                    <span class="presets-panel-meta">
                      {{ p.workout_type }}
                      <template v-if="p.duration_minutes"> · {{ p.duration_minutes }}m</template>
                      <template v-if="p.exercises.length > 0"> · {{ p.exercises.length }} ex.</template>
                    </span>
                  </div>
                  <div class="presets-panel-actions">
                    <button class="presets-panel-btn" @click="openEditPreset(p.id)" title="Modifier">
                      <Pencil :size="13" />
                    </button>
                    <button class="presets-panel-btn presets-panel-btn-danger" @click="handleDeletePreset(p.id)" title="Supprimer">
                      <Trash2 :size="13" />
                    </button>
                  </div>
                </div>
              </div>
              <router-link to="/workouts/presets" class="presets-see-all">
                Voir tous les presets
                <ArrowRight :size="13" />
              </router-link>
            </div>
          </div>
        </div>
      </template>
    </main>

    <!-- Create/Edit Dialog -->
    <Dialog v-model:open="showDialog">
      <DialogContent class="dialog-wide">
        <DialogHeader>
          <DialogTitle>{{ editingId ? 'Modifier la séance' : 'Nouvelle séance' }}</DialogTitle>
          <DialogDescription>
            {{ editingId ? 'Modifiez les détails de la séance.' : 'Enregistrez une séance de sport.' }}
          </DialogDescription>
        </DialogHeader>
        <div class="dialog-form">
          <!-- Presets section -->
          <div v-if="presets.length > 0" class="presets-section">
            <div class="presets-header">
              <button class="presets-toggle" @click="showPresetDropdown = !showPresetDropdown" type="button">
                <Bookmark :size="14" />
                <span>Charger un preset</span>
                <ChevronDown :size="12" class="presets-chevron" :class="{ rotated: showPresetDropdown }" />
              </button>
            </div>
            <div v-if="showPresetDropdown" class="presets-list">
              <div v-for="p in presets" :key="p.id" class="preset-item">
                <button class="preset-btn" @mousedown="loadPreset(p.id)" type="button">
                  <span class="preset-name">{{ p.name }}</span>
                  <span class="preset-meta">{{ p.workout_type }}<template v-if="p.duration_minutes"> · {{ p.duration_minutes }}m</template></span>
                </button>
                <button class="preset-delete" @mousedown.stop="handleDeletePreset(p.id)" type="button" title="Supprimer">
                  <Trash2 :size="12" />
                </button>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field form-field-grow">
              <label>Nom de la séance</label>
              <div class="type-input-wrapper">
                <Input
                  v-model="formType"
                  placeholder="ex. Course, Musculation"
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
              <label>Durée (min)</label>
              <Input v-model="formDuration" type="number" placeholder="—" style="width: 90px" />
            </div>
          </div>
          <div class="form-field">
            <label>Notes</label>
            <Input v-model="formNotes" placeholder="Notes facultatives" />
          </div>

          <!-- Exercises section -->
          <div class="exercises-section">
            <div class="exercises-header">
              <label>Exercices</label>
              <Button variant="ghost" size="sm" @click="addExercise" type="button">
                <Plus :size="14" />
                Ajouter
              </Button>
            </div>
            <div v-if="formExercises.length === 0" class="exercises-empty">
              Aucun exercice. Cliquez sur « Ajouter » pour en ajouter.
            </div>
            <div v-else class="exercises-list">
              <div v-for="(ex, i) in formExercises" :key="i" class="exercise-row">
                <div class="exercise-inputs">
                  <Input
                    v-model="ex.name"
                    placeholder="Nom de l'exercice"
                    class="exercise-name-input"
                  />
                  <Input
                    v-model="ex.notes"
                    placeholder="Détails (ex. 3x12 @ 60kg)"
                    class="exercise-notes-input"
                  />
                </div>
                <Button variant="ghost" size="sm" @click="removeExercise(i)" type="button" class="exercise-remove">
                  <X :size="14" />
                </Button>
              </div>
            </div>
          </div>
        </div>
        <!-- Save as preset -->
        <div class="save-preset-section">
          <label class="save-preset-check">
            <input type="checkbox" v-model="saveAsPreset" />
            <span>Sauvegarder comme preset</span>
          </label>
          <Input
            v-if="saveAsPreset"
            v-model="presetName"
            placeholder="Nom du preset"
            class="preset-name-input"
          />
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showDialog = false">Annuler</Button>
          <Button @click="saveWorkout" :disabled="!formType.trim()">
            {{ editingId ? 'Enregistrer' : 'Ajouter' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Preset Create/Edit Dialog -->
    <Dialog v-model:open="showPresetDialog">
      <DialogContent class="dialog-wide">
        <DialogHeader>
          <DialogTitle>{{ editingPresetId ? 'Modifier le preset' : 'Nouveau preset' }}</DialogTitle>
          <DialogDescription>
            {{ editingPresetId ? 'Modifiez les détails du preset.' : 'Créez un preset réutilisable.' }}
          </DialogDescription>
        </DialogHeader>
        <div class="dialog-form">
          <div class="form-field">
            <label>Nom du preset</label>
            <Input v-model="presetFormName" placeholder="Nom du preset" />
          </div>
          <div class="form-row">
            <div class="form-field form-field-grow">
              <label>Type de séance</label>
              <Input v-model="presetFormType" placeholder="ex. Musculation" />
            </div>
            <div class="form-field">
              <label>Durée (min)</label>
              <Input v-model="presetFormDuration" type="number" placeholder="—" style="width: 90px" />
            </div>
          </div>

          <div class="exercises-section">
            <div class="exercises-header">
              <label>Exercices</label>
              <Button variant="ghost" size="sm" @click="addPresetExercise" type="button">
                <Plus :size="14" />
                Ajouter
              </Button>
            </div>
            <div v-if="presetFormExercises.length === 0" class="exercises-empty">
              Aucun exercice.
            </div>
            <div v-else class="exercises-list">
              <div v-for="(ex, i) in presetFormExercises" :key="i" class="exercise-row">
                <div class="exercise-inputs">
                  <Input v-model="ex.name" placeholder="Nom de l'exercice" class="exercise-name-input" />
                  <Input v-model="ex.notes" placeholder="Détails (ex. 3x12 @ 60kg)" class="exercise-notes-input" />
                </div>
                <Button variant="ghost" size="sm" @click="removePresetExercise(i)" type="button" class="exercise-remove">
                  <X :size="14" />
                </Button>
              </div>
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showPresetDialog = false">Annuler</Button>
          <Button @click="savePresetForm" :disabled="!presetFormName.trim() || !presetFormType.trim()">
            {{ editingPresetId ? 'Enregistrer' : 'Créer' }}
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
  transition: border-color 0.15s, box-shadow 0.15s;
}

.summary-stat:hover {
  border-color: var(--app-border-hover);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.stat-icon {
  color: var(--theme-accent);
}

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.stat-label {
  display: block;
  font-size: 0.72rem;
  color: var(--app-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-weight: 500;
}

.workout-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: stretch;
}

.calendar-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Date detail panel */
.date-detail {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 16px 20px;
}

.date-detail-title {
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0 0 12px;
  text-transform: capitalize;
}

.date-detail-empty {
  color: var(--app-text-muted);
  font-size: 0.85rem;
}

.date-detail-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.date-session {
  padding: 10px 12px;
  background: var(--app-surface-2);
  border-radius: 8px;
}

.date-session-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}

.date-session-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.date-session-type {
  font-weight: 600;
  font-size: 0.88rem;
}

.date-session-duration {
  font-size: 0.75rem;
  color: var(--app-text-muted);
}

.date-session-chevron {
  color: var(--app-text-dim);
  transition: transform 0.15s ease;
}

.date-session-chevron.rotated {
  transform: rotate(180deg);
}

.date-session-body {
  padding-top: 8px;
}

.date-session-notes {
  margin: 0 0 4px;
  font-size: 0.8rem;
  color: var(--app-text-muted);
}

.date-session-exercises {
  margin-top: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date-exercise {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 4px 0;
  border-top: 1px solid var(--app-border);
}

.date-exercise-name {
  font-size: 0.82rem;
  font-weight: 500;
}

.date-exercise-notes {
  font-size: 0.75rem;
  color: var(--app-text-muted);
}

/* Dialog form */
.dialog-wide {
  max-width: 540px;
}

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 8px 0;
}

.form-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-field-grow {
  flex: 1;
}

.form-field label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--app-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
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

/* Exercises in dialog */
.exercises-section {
  border-top: 1px solid var(--app-border);
  padding-top: 12px;
}

.exercises-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.exercises-header label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--app-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.exercises-empty {
  color: var(--app-text-muted);
  font-size: 0.82rem;
  text-align: center;
  padding: 12px 0;
}

.exercises-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.exercise-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.exercise-inputs {
  display: flex;
  gap: 8px;
  flex: 1;
}

.exercise-name-input {
  flex: 1;
}

.exercise-notes-input {
  flex: 1;
}

.exercise-remove {
  flex-shrink: 0;
  color: var(--app-text-muted);
}

/* Right column — stretches to match left, splits evenly */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-title {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--app-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.panel-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel-title-row .panel-title {
  margin: 0;
}

/* History panel — card with title inside, fills available space */
.history-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 20px;
  min-height: 0;
}

.history-scroll {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* Remove WorkoutHistory's own card styling — the parent is the card */
.history-panel :deep(.workout-history) {
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.history-panel :deep(.history-list) {
  flex: 1;
  max-height: none;
  overflow-y: auto;
}

/* Presets panel — takes remaining space, list scrolls */
.presets-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 16px 20px;
  min-height: 0;
  overflow: hidden;
}

.presets-panel-empty {
  color: var(--app-text-muted);
  font-size: 0.82rem;
  text-align: center;
  padding: 12px 0;
}

.presets-panel-scroll {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
  min-height: 0;
}

.presets-see-all {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 0 2px;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--app-text-muted);
  text-decoration: none;
  transition: color 0.15s;
  flex-shrink: 0;
}

.presets-see-all:hover {
  color: var(--app-text);
}

.presets-panel-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  transition: background 0.15s;
}

.presets-panel-item:hover {
  background: var(--app-surface-2);
}

.presets-panel-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.presets-panel-name {
  font-size: 0.88rem;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.presets-panel-meta {
  font-size: 0.72rem;
  color: var(--app-text-dim);
}

.presets-panel-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.presets-panel-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: var(--app-text-dim);
  transition: color 0.1s, background 0.1s;
}

.presets-panel-btn:hover {
  color: var(--app-text);
  background: var(--app-surface-3);
}

.presets-panel-btn-danger:hover {
  color: #dc2626;
  background: var(--app-surface-3);
}

/* Presets in dialog */
.presets-section {
  border-bottom: 1px solid var(--app-border);
  padding-bottom: 12px;
}

.presets-header {
  display: flex;
  align-items: center;
}

.presets-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--app-text-muted);
  padding: 0;
}

.presets-toggle:hover {
  color: var(--app-text);
}

.presets-chevron {
  transition: transform 0.15s ease;
}

.presets-chevron.rotated {
  transform: rotate(180deg);
}

.presets-list {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: var(--app-surface-2);
  border-radius: 8px;
  padding: 4px;
  max-height: 160px;
  overflow-y: auto;
}

.preset-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.preset-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1px;
  text-align: left;
  padding: 8px 10px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.1s;
}

.preset-btn:hover {
  background: var(--app-surface);
}

.preset-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--app-text);
}

.preset-meta {
  font-size: 0.72rem;
  color: var(--app-text-dim);
}

.preset-delete {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: var(--app-text-dim);
  transition: color 0.1s, background 0.1s;
}

.preset-delete:hover {
  color: #dc2626;
  background: var(--app-surface);
}

/* Save as preset */
.save-preset-section {
  border-top: 1px solid var(--app-border);
  padding-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.save-preset-check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  color: var(--app-text-muted);
  cursor: pointer;
}

.save-preset-check input[type="checkbox"] {
  accent-color: var(--theme-accent);
}

.preset-name-input {
  max-width: 280px;
}

@media (max-width: 768px) {
  .workout-grid {
    grid-template-columns: 1fr;
  }

  .summary-row {
    flex-direction: column;
  }

  .content {
    padding: 24px 16px 88px;
  }

  .form-row {
    flex-direction: column;
    align-items: stretch;
  }

  .exercise-inputs {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .content {
    padding: 16px 12px 88px;
  }

  .page-header h1 {
    font-size: 1.4rem;
  }

  .summary-stat {
    padding: 12px 14px;
  }

  .stat-value {
    font-size: 1.1rem;
  }

  .preset-name-input {
    max-width: 100%;
  }

  .date-detail {
    padding: 12px 14px;
  }

  .history-panel {
    padding: 14px;
  }

  .presets-panel {
    padding: 12px 14px;
  }
}
</style>
