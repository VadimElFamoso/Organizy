<script setup lang="ts">
import { ref, watch } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus } from 'lucide-vue-next'
import KanbanColumn from './KanbanColumn.vue'
import ColorPicker from './ColorPicker.vue'
import type { TaskItem, ProjectColumn } from '@/services/api'

const props = defineProps<{
  projectId: string
  columns: ProjectColumn[]
  itemsByColumn: Record<string, TaskItem[]>
}>()

const emit = defineEmits<{
  toggle: [id: string]
  delete: [id: string]
  reorder: [items: { id: string; column_id?: string | null; sort_order: number }[]]
  addColumn: [name: string, color?: string]
  updateColumn: [columnId: string, data: { name?: string; color?: string }]
  deleteColumn: [columnId: string]
  reorderColumns: [items: { id: string; sort_order: number }[]]
  openDetail: [task: TaskItem]
}>()

const showAddColumn = ref(false)
const newColumnName = ref('')
const newColumnColor = ref('#78716c')

// Local copy for column DnD
const localColumns = ref<ProjectColumn[]>([])

function syncColumns() {
  localColumns.value = [...props.columns]
}

watch(() => props.columns, syncColumns, { immediate: true, deep: true })

function handleAddColumn() {
  if (!newColumnName.value.trim()) return
  emit('addColumn', newColumnName.value.trim(), newColumnColor.value)
  newColumnName.value = ''
  newColumnColor.value = '#78716c'
  showAddColumn.value = false
}

function handleColumnUpdate(columnId: string, items: TaskItem[]) {
  const reorderItems = items.map((item, index) => ({
    id: item.id,
    column_id: columnId,
    sort_order: index,
  }))
  emit('reorder', reorderItems)
}

function handleColumnDnD(newOrder: ProjectColumn[]) {
  localColumns.value = newOrder
  const reorderItems = newOrder.map((col, index) => ({
    id: col.id,
    sort_order: index,
  }))
  emit('reorderColumns', reorderItems)
}
</script>

<template>
  <div class="kanban-wrapper">
    <VueDraggable
      :model-value="localColumns"
      @update:model-value="handleColumnDnD"
      class="kanban-board"
      handle=".column-header"
      :animation="200"
      item-key="id"
    >
      <KanbanColumn
        v-for="col in localColumns"
        :key="col.id"
        :title="col.name"
        :column-id="col.id"
        :color="col.color"
        :items="itemsByColumn[col.id] || []"
        :can-edit="true"
        :can-delete="true"
        @update:items="handleColumnUpdate(col.id, $event)"
        @toggle="emit('toggle', $event)"
        @delete="emit('delete', $event)"
        @update-column="(data) => emit('updateColumn', col.id, data)"
        @delete-column="emit('deleteColumn', col.id)"
        @open-detail="emit('openDetail', $event)"
      />
    </VueDraggable>

    <!-- Add column — always next to last column -->
    <div class="add-column">
      <div v-if="showAddColumn" class="add-column-form">
        <Input
          v-model="newColumnName"
          placeholder="Nom de la colonne..."
          size="sm"
          @keyup.enter="handleAddColumn"
          @keyup.escape="showAddColumn = false"
        />
        <ColorPicker v-model="newColumnColor" />
        <div class="add-actions">
          <Button size="sm" @click="handleAddColumn" :disabled="!newColumnName.trim()">Ajouter</Button>
          <Button variant="ghost" size="sm" @click="showAddColumn = false">Annuler</Button>
        </div>
      </div>
      <Button v-else variant="ghost" size="sm" class="add-column-btn" @click="showAddColumn = true">
        <Plus :size="14" />
        Colonne
      </Button>
    </div>
  </div>
</template>

<style scoped>
.kanban-wrapper {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  min-height: 300px;
}

.kanban-board {
  display: contents;
}

.add-column-form {
  background: var(--app-surface-2);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.add-actions {
  display: flex;
  gap: 4px;
}

.add-column-btn {
  width: 100%;
  height: 100%;
  min-height: 100px;
  justify-content: center;
  border: 1px dashed var(--app-border);
  border-radius: 12px;
  padding: 20px;
  color: var(--app-text-dim);
}

.add-column-btn:hover {
  border-color: var(--app-border-hover);
  color: var(--app-text-muted);
}

@media (max-width: 768px) {
  .kanban-wrapper {
    grid-template-columns: 1fr;
  }
}
</style>
