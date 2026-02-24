<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus } from 'lucide-vue-next'
import type { ProjectColumn, ProjectMethod } from '@/services/api'

const props = defineProps<{
  method: ProjectMethod
  columns: ProjectColumn[]
}>()

const emit = defineEmits<{
  create: [data: { title: string; description?: string; column_id?: string; priority?: string; due_date?: string }]
}>()

const open = ref(false)
const title = ref('')
const description = ref('')
const columnId = ref('')
const priority = ref('medium')
const dueDate = ref('')

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
// columns[0..1] = column headers, columns[2..3] = row headers
// Quadrant mapping: col[0]→(0,2), col[1]→(1,2), col[2]→(0,3), col[3]→(1,3)
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

function reset() {
  title.value = ''
  description.value = ''
  columnId.value = props.columns[0]?.id || ''
  priority.value = 'medium'
  dueDate.value = ''
}

function handleCreate() {
  if (!title.value.trim()) return

  const data: { title: string; description?: string; column_id?: string; priority?: string; due_date?: string } = {
    title: title.value.trim(),
  }

  if (description.value.trim()) data.description = description.value.trim()
  if (showColumnSelector.value && columnId.value) data.column_id = columnId.value
  if (showPrioritySelector.value && priority.value) data.priority = priority.value
  if (showDueDate.value && dueDate.value) data.due_date = dueDate.value

  emit('create', data)
  reset()
  open.value = false
}

function onOpen(val: boolean) {
  open.value = val
  if (val) {
    columnId.value = props.columns[0]?.id || ''
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="onOpen">
    <DialogTrigger as-child>
      <Button size="sm">
        <Plus :size="14" />
        Tâche
      </Button>
    </DialogTrigger>
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Nouvelle tâche</DialogTitle>
        <DialogDescription>Ajoutez une tâche à ce projet.</DialogDescription>
      </DialogHeader>

      <div class="form">
        <Input
          v-model="title"
          placeholder="Titre de la tâche..."
          @keyup.enter="handleCreate"
        />

        <textarea
          v-model="description"
          placeholder="Description (optionnel)..."
          class="textarea"
          rows="2"
        />

        <!-- Column / Quadrant selector -->
        <div v-if="showColumnSelector" class="field">
          <label class="field-label">
            {{ method === 'eisenhower' ? 'Quadrant' : 'Colonne' }}
          </label>
          <div class="column-options">
            <button
              v-for="col in displayColumns"
              :key="col.id"
              class="column-option"
              :class="{ active: columnId === col.id }"
              @click="columnId = col.id"
            >
              <div class="col-dot" :style="{ background: col.color }" />
              {{ (col as any).displayName || col.name }}
            </button>
          </div>
        </div>

        <!-- Priority selector (classic only) -->
        <div v-if="showPrioritySelector" class="field">
          <label class="field-label">Priorité</label>
          <div class="column-options">
            <button
              v-for="p in priorities"
              :key="p.value"
              class="column-option"
              :class="{ active: priority === p.value }"
              @click="priority = p.value"
            >
              <div class="col-dot" :style="{ background: p.color }" />
              {{ p.label }}
            </button>
          </div>
        </div>

        <!-- Due date -->
        <div v-if="showDueDate" class="field">
          <label class="field-label">Échéance (optionnel)</label>
          <Input v-model="dueDate" type="date" />
        </div>

        <Button @click="handleCreate" :disabled="!title.trim()" class="create-btn">
          Ajouter
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.textarea {
  width: 100%;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.875rem;
  font-family: inherit;
  resize: vertical;
  background: var(--app-surface);
  color: var(--app-text);
}

.textarea:focus {
  outline: none;
  border-color: var(--app-text);
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

.column-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.column-option {
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

.column-option:hover {
  border-color: var(--app-border-hover);
}

.column-option.active {
  border-color: var(--app-text);
  background: var(--app-surface-2);
}

.col-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.create-btn {
  width: 100%;
}
</style>
