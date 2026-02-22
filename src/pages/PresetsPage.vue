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
import { Plus, X, Pencil, Trash2, Bookmark, ChevronDown, ArrowLeft, Dumbbell, Clock } from 'lucide-vue-next'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const {
  presets,
  fetchPresets,
  createPreset,
  updatePreset,
  deletePreset,
} = useWorkouts()

const showDialog = ref(false)
const editingPresetId = ref<string | null>(null)
const formName = ref('')
const formType = ref('')
const formDuration = ref<string>('')
const formExercises = ref<{ name: string; notes: string }[]>([])
const expandedPreset = ref<string | null>(null)

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }
  await fetchPresets()
})

function openCreate() {
  editingPresetId.value = null
  formName.value = ''
  formType.value = ''
  formDuration.value = ''
  formExercises.value = []
  showDialog.value = true
}

function openEdit(presetId: string) {
  const p = presets.value.find(p => p.id === presetId)
  if (!p) return
  editingPresetId.value = presetId
  formName.value = p.name
  formType.value = p.workout_type
  formDuration.value = p.duration_minutes?.toString() || ''
  formExercises.value = p.exercises.map(ex => ({ name: ex.name, notes: ex.notes || '' }))
  showDialog.value = true
}

function addExercise() {
  formExercises.value.push({ name: '', notes: '' })
}

function removeExercise(index: number) {
  formExercises.value.splice(index, 1)
}

async function saveForm() {
  if (!formName.value.trim() || !formType.value.trim()) return
  const exercises = formExercises.value
    .filter(ex => ex.name.trim())
    .map((ex, i) => ({
      name: ex.name.trim(),
      notes: ex.notes.trim() || undefined,
      sort_order: i,
    }))
  if (editingPresetId.value) {
    await updatePreset(editingPresetId.value, {
      name: formName.value.trim(),
      workout_type: formType.value.trim(),
      duration_minutes: formDuration.value ? parseInt(formDuration.value) : null,
      exercises,
    })
  } else {
    await createPreset({
      name: formName.value.trim(),
      workout_type: formType.value.trim(),
      duration_minutes: formDuration.value ? parseInt(formDuration.value) : undefined,
      exercises,
    })
  }
  showDialog.value = false
}

async function handleDelete(presetId: string) {
  await deletePreset(presetId)
}

function toggleExpand(id: string) {
  expandedPreset.value = expandedPreset.value === id ? null : id
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
        <div class="page-header-left">
          <button class="back-btn" @click="router.back()">
            <ArrowLeft :size="18" />
          </button>
          <h1>Presets</h1>
        </div>
        <Button @click="openCreate" size="sm">
          <Plus :size="16" />
          Nouveau preset
        </Button>
      </div>

      <div v-if="presets.length === 0" class="empty-state">
        <Bookmark :size="32" class="empty-icon" />
        <p>Aucun preset pour le moment.</p>
        <p class="empty-sub">Créez des presets pour remplir vos séances en un clic.</p>
      </div>

      <div v-else class="preset-grid">
        <div v-for="p in presets" :key="p.id" class="preset-card">
          <div class="preset-card-header" @click="toggleExpand(p.id)">
            <div class="preset-card-info">
              <span class="preset-card-name">{{ p.name }}</span>
              <div class="preset-card-meta">
                <span class="preset-card-type">
                  <Dumbbell :size="12" />
                  {{ p.workout_type }}
                </span>
                <span v-if="p.duration_minutes" class="preset-card-duration">
                  <Clock :size="12" />
                  {{ p.duration_minutes }}m
                </span>
                <span v-if="p.exercises.length > 0" class="preset-card-count">
                  {{ p.exercises.length }} exercice{{ p.exercises.length > 1 ? 's' : '' }}
                </span>
              </div>
            </div>
            <div class="preset-card-actions">
              <button class="card-action-btn" @click.stop="openEdit(p.id)" title="Modifier">
                <Pencil :size="14" />
              </button>
              <button class="card-action-btn card-action-danger" @click.stop="handleDelete(p.id)" title="Supprimer">
                <Trash2 :size="14" />
              </button>
              <ChevronDown
                v-if="p.exercises.length > 0"
                :size="14"
                class="card-chevron"
                :class="{ rotated: expandedPreset === p.id }"
              />
            </div>
          </div>
          <div v-if="expandedPreset === p.id && p.exercises.length > 0" class="preset-card-body">
            <div v-for="ex in p.exercises" :key="ex.id || ex.sort_order" class="preset-exercise">
              <span class="preset-exercise-name">{{ ex.name }}</span>
              <span v-if="ex.notes" class="preset-exercise-notes">{{ ex.notes }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Create/Edit Dialog -->
    <Dialog v-model:open="showDialog">
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
            <Input v-model="formName" placeholder="Nom du preset" />
          </div>
          <div class="form-row">
            <div class="form-field form-field-grow">
              <label>Type de séance</label>
              <Input v-model="formType" placeholder="ex. Musculation" />
            </div>
            <div class="form-field">
              <label>Durée (min)</label>
              <Input v-model="formDuration" type="number" placeholder="—" style="width: 90px" />
            </div>
          </div>

          <div class="exercises-section">
            <div class="exercises-header">
              <label>Exercices</label>
              <Button variant="ghost" size="sm" @click="addExercise" type="button">
                <Plus :size="14" />
                Ajouter
              </Button>
            </div>
            <div v-if="formExercises.length === 0" class="exercises-empty">
              Aucun exercice.
            </div>
            <div v-else class="exercises-list">
              <div v-for="(ex, i) in formExercises" :key="i" class="exercise-row">
                <div class="exercise-inputs">
                  <Input v-model="ex.name" placeholder="Nom de l'exercice" class="exercise-name-input" />
                  <Input v-model="ex.notes" placeholder="Détails (ex. 3x12 @ 60kg)" class="exercise-notes-input" />
                </div>
                <Button variant="ghost" size="sm" @click="removeExercise(i)" type="button" class="exercise-remove">
                  <X :size="14" />
                </Button>
              </div>
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showDialog = false">Annuler</Button>
          <Button @click="saveForm" :disabled="!formName.trim() || !formType.trim()">
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
  max-width: 700px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.page-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  cursor: pointer;
  color: var(--app-text-muted);
  transition: border-color 0.15s, color 0.15s;
}

.back-btn:hover {
  border-color: var(--app-border-hover);
  color: var(--app-text);
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 64px 24px;
  color: var(--app-text-muted);
}

.empty-icon {
  color: var(--app-text-dim);
  margin-bottom: 16px;
}

.empty-state p {
  margin: 0;
  font-size: 0.95rem;
}

.empty-sub {
  font-size: 0.82rem !important;
  color: var(--app-text-dim);
  margin-top: 4px !important;
}

/* Preset grid */
.preset-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.preset-card {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.preset-card:hover {
  border-color: var(--app-border-hover);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.preset-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  cursor: pointer;
  user-select: none;
}

.preset-card-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.preset-card-name {
  font-size: 0.95rem;
  font-weight: 600;
}

.preset-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.preset-card-type,
.preset-card-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.78rem;
  color: var(--app-text-muted);
}

.preset-card-count {
  font-size: 0.72rem;
  color: var(--app-text-dim);
  background: var(--app-surface-3);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.preset-card-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.card-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: var(--app-text-dim);
  transition: color 0.1s, background 0.1s;
}

.card-action-btn:hover {
  color: var(--app-text);
  background: var(--app-surface-2);
}

.card-action-danger:hover {
  color: #dc2626;
}

.card-chevron {
  color: var(--app-text-dim);
  transition: transform 0.15s ease;
  margin-left: 4px;
}

.card-chevron.rotated {
  transform: rotate(180deg);
}

/* Expanded exercises */
.preset-card-body {
  padding: 0 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preset-exercise {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 6px 10px;
  background: var(--app-surface-2);
  border-radius: 6px;
}

.preset-exercise-name {
  font-size: 0.82rem;
  font-weight: 500;
}

.preset-exercise-notes {
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

@media (max-width: 768px) {
  .content {
    padding: 24px 16px;
  }

  .form-row {
    flex-direction: column;
    align-items: stretch;
  }

  .exercise-inputs {
    flex-direction: column;
  }
}
</style>
