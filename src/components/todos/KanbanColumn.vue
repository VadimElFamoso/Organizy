<script setup lang="ts">
import { ref } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus } from 'lucide-vue-next'
import KanbanCard from './KanbanCard.vue'
import type { TodoItem } from '@/services/api'

const props = defineProps<{
  title: string
  priority: string
  items: TodoItem[]
}>()

const emit = defineEmits<{
  'update:items': [items: TodoItem[]]
  add: [priority: string, title: string]
  toggle: [id: string]
  delete: [id: string]
}>()

const showAdd = ref(false)
const newTitle = ref('')

function handleAdd() {
  if (!newTitle.value.trim()) return
  emit('add', props.priority, newTitle.value.trim())
  newTitle.value = ''
  showAdd.value = false
}

function onUpdate(items: TodoItem[]) {
  emit('update:items', items)
}

const priorityColors: Record<string, string> = {
  urgent: '#dc2626',
  high: '#ea580c',
  medium: '#78716c',
  low: '#a8a29e',
}
</script>

<template>
  <div class="kanban-column">
    <div class="column-header">
      <div class="header-left">
        <div class="priority-dot" :style="{ background: priorityColors[priority] || '#78716c' }" />
        <span class="column-title">{{ title }}</span>
        <span class="column-count">{{ items.length }}</span>
      </div>
      <Button variant="ghost" size="sm" @click="showAdd = !showAdd">
        <Plus :size="14" />
      </Button>
    </div>

    <div v-if="showAdd" class="add-form">
      <Input
        v-model="newTitle"
        placeholder="Titre de la tâche..."
        size="sm"
        @keyup.enter="handleAdd"
        @keyup.escape="showAdd = false"
      />
      <div class="add-actions">
        <Button size="sm" @click="handleAdd" :disabled="!newTitle.trim()">Ajouter</Button>
        <Button variant="ghost" size="sm" @click="showAdd = false">Annuler</Button>
      </div>
    </div>

    <VueDraggable
      :model-value="items"
      @update:model-value="onUpdate"
      group="kanban"
      class="column-content"
      item-key="id"
      :animation="150"
      ghost-class="ghost"
    >
      <KanbanCard
        v-for="todo in items"
        :key="todo.id"
        :todo="todo"
        @toggle="emit('toggle', $event)"
        @delete="emit('delete', $event)"
      />
    </VueDraggable>
  </div>
</template>

<style scoped>
.kanban-column {
  background: var(--app-surface-2, #f5f2ed);
  border-radius: 12px;
  padding: 12px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 0 4px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.priority-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.column-title {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--app-text-dim);
}

.column-count {
  font-size: 0.65rem;
  color: var(--app-text-muted);
  background: var(--app-surface-3);
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 500;
}

.add-form {
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.add-actions {
  display: flex;
  gap: 4px;
}

.column-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 50px;
}

.ghost {
  opacity: 0.4;
}
</style>
