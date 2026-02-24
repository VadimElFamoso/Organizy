<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Trash2 } from 'lucide-vue-next'
import type { TaskItem, ProjectColumn, ProjectMethod } from '@/services/api'

const props = defineProps<{
  task: TaskItem | null
  open: boolean
  method: ProjectMethod
  columns: ProjectColumn[]
}>()

const emit = defineEmits<{
  'update:open': [val: boolean]
  save: [id: string, data: Partial<{ title: string; description: string | null; column_id: string | null; priority: string | null; due_date: string | null }>]
  delete: [id: string]
}>()

const editTitle = ref('')
const editDescription = ref('')
const editColumnId = ref('')
const editPriority = ref('')
const editDueDate = ref('')

const priorities = [
  { value: 'low', label: 'Basse', color: '#a8a29e' },
  { value: 'medium', label: 'Moyenne', color: '#78716c' },
  { value: 'high', label: 'Haute', color: '#ea580c' },
  { value: 'urgent', label: 'Urgent', color: '#dc2626' },
]

const showColumnSelector = computed(() => props.method === 'kanban' || props.method === 'eisenhower')
const showPrioritySelector = computed(() => props.method === 'classic')
const showDueDate = computed(() => props.method === 'kanban' || props.method === 'classic')

// For Eisenhower: compose quadrant names from axis labels
const displayColumns = computed(() => {
  if (props.method !== 'eisenhower' || props.columns.length < 4) return props.columns
  const cols = props.columns
  return [
    { ...cols[0], displayName: cols[0].name + ' & ' + cols[2].name },
    { ...cols[1], displayName: cols[1].name + ' & ' + cols[2].name },
    { ...cols[2], displayName: cols[0].name + ' & ' + cols[3].name },
    { ...cols[3], displayName: cols[1].name + ' & ' + cols[3].name },
  ]
})

watch(() => props.task, (task) => {
  if (task) {
    editTitle.value = task.title
    editDescription.value = task.description || ''
    editColumnId.value = task.column_id || ''
    editPriority.value = task.priority || 'medium'
    editDueDate.value = task.due_date || ''
  }
})

function handleSave() {
  if (!props.task || !editTitle.value.trim()) return

  const data: Partial<{ title: string; description: string | null; column_id: string | null; priority: string | null; due_date: string | null }> = {}

  if (editTitle.value.trim() !== props.task.title) {
    data.title = editTitle.value.trim()
  }
  const newDesc = editDescription.value.trim() || null
  if (newDesc !== (props.task.description || null)) {
    data.description = newDesc
  }
  if (showColumnSelector.value && editColumnId.value !== (props.task.column_id || '')) {
    data.column_id = editColumnId.value || null
  }
  if (showPrioritySelector.value && editPriority.value !== (props.task.priority || 'medium')) {
    data.priority = editPriority.value || null
  }
  if (showDueDate.value) {
    const newDate = editDueDate.value || null
    if (newDate !== (props.task.due_date || null)) {
      data.due_date = newDate
    }
  }

  if (Object.keys(data).length > 0) {
    emit('save', props.task.id, data)
  }
  emit('update:open', false)
}

function handleDelete() {
  if (!props.task) return
  emit('delete', props.task.id)
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Détails de la tâche</DialogTitle>
        <DialogDescription>Modifiez les informations de cette tâche.</DialogDescription>
      </DialogHeader>

      <div v-if="task" class="detail-form">
        <div class="field">
          <label class="field-label">Titre</label>
          <Input v-model="editTitle" placeholder="Titre..." />
        </div>

        <div class="field">
          <label class="field-label">Description</label>
          <Textarea v-model="editDescription" placeholder="Description (optionnel)..." :rows="3" />
        </div>

        <!-- Column / Quadrant selector -->
        <div v-if="showColumnSelector" class="field">
          <label class="field-label">
            {{ method === 'eisenhower' ? 'Quadrant' : 'Colonne' }}
          </label>
          <div class="option-group">
            <button
              v-for="col in displayColumns"
              :key="col.id"
              class="option-btn"
              :class="{ active: editColumnId === col.id }"
              @click="editColumnId = col.id"
            >
              <div class="dot" :style="{ background: col.color }" />
              {{ (col as any).displayName || col.name }}
            </button>
          </div>
        </div>

        <!-- Priority selector (classic) -->
        <div v-if="showPrioritySelector" class="field">
          <label class="field-label">Priorité</label>
          <div class="option-group">
            <button
              v-for="p in priorities"
              :key="p.value"
              class="option-btn"
              :class="{ active: editPriority === p.value }"
              @click="editPriority = p.value"
            >
              <div class="dot" :style="{ background: p.color }" />
              {{ p.label }}
            </button>
          </div>
        </div>

        <!-- Due date -->
        <div v-if="showDueDate" class="field">
          <label class="field-label">Échéance</label>
          <Input v-model="editDueDate" type="date" />
        </div>

        <div class="actions">
          <Button @click="handleSave" :disabled="!editTitle.trim()">Enregistrer</Button>
          <Button variant="destructive" @click="handleDelete">
            <Trash2 :size="14" />
            Supprimer
          </Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>

<style scoped>
.detail-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 8px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--app-text-dim);
}

.option-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--app-border);
  border-radius: 6px;
  background: var(--app-surface);
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.15s;
}

.option-btn:hover {
  border-color: var(--app-border-hover);
}

.option-btn.active {
  border-color: var(--app-text);
  background: var(--app-surface-2);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.actions {
  display: flex;
  gap: 8px;
  padding-top: 8px;
}
</style>
