<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Input } from '@/components/ui/input'
import { Pencil } from 'lucide-vue-next'
import EisenhowerQuadrant from './EisenhowerQuadrant.vue'
import ColorPicker from './ColorPicker.vue'
import type { TaskItem, ProjectColumn } from '@/services/api'

const props = defineProps<{
  columns: ProjectColumn[]
  itemsByColumn: Record<string, TaskItem[]>
}>()

const emit = defineEmits<{
  toggle: [id: string]
  delete: [id: string]
  reorder: [items: { id: string; column_id?: string | null; sort_order: number }[]]
  updateColumn: [columnId: string, data: { name?: string; color?: string }]
  openDetail: [task: TaskItem]
}>()

// Track mobile breakpoint to show quadrant titles when axis labels are hidden
const isMobile = ref(window.innerWidth <= 768)

function onResize() {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))

// Editing state for axis labels
const editingLabel = ref<number | null>(null)
const editLabelName = ref('')
const editLabelColor = ref('')
const editLabelRef = ref<HTMLElement | null>(null)

function startEditLabel(index: number) {
  const col = props.columns[index]
  if (!col) return
  editLabelName.value = col.name
  editLabelColor.value = col.color
  editingLabel.value = index
}

function saveLabel() {
  if (editingLabel.value === null) return
  const col = props.columns[editingLabel.value]
  if (!col) { editingLabel.value = null; return }

  const data: { name?: string; color?: string } = {}
  if (editLabelName.value.trim() && editLabelName.value.trim() !== col.name) {
    data.name = editLabelName.value.trim()
  }
  if (editLabelColor.value && editLabelColor.value !== col.color) {
    data.color = editLabelColor.value
  }
  if (Object.keys(data).length > 0) {
    emit('updateColumn', col.id, data)
  }
  editingLabel.value = null
}

function handleLabelFocusOut(e: FocusEvent) {
  const related = e.relatedTarget as Node | null
  if (editLabelRef.value && related && editLabelRef.value.contains(related)) return
  saveLabel()
}

function handleQuadrantUpdate(columnId: string, items: TaskItem[]) {
  const reorderItems = items.map((item, index) => ({
    id: item.id,
    column_id: columnId,
    sort_order: index,
  }))
  emit('reorder', reorderItems)
}
</script>

<template>
  <div class="eisenhower-table">
    <!-- Corner cell -->
    <div class="corner-cell" />

    <!-- Top column labels: columns[0] and columns[1] -->
    <div v-for="i in [0, 1]" :key="'col-' + i" class="axis-label col-label">
      <template v-if="columns[i]">
        <template v-if="editingLabel === i">
          <div ref="editLabelRef" class="label-edit" @focusout="handleLabelFocusOut">
            <Input
              v-model="editLabelName"
              class="label-input"
              size="sm"
              @keyup.enter="saveLabel"
              @keyup.escape="editingLabel = null"
            />
            <ColorPicker v-model="editLabelColor" />
          </div>
        </template>
        <template v-else>
          <span class="label-text" @click="startEditLabel(i)">
            <span class="label-dot" :style="{ background: columns[i].color }" />
            {{ columns[i].name }}
            <Pencil :size="9" class="label-edit-icon" />
          </span>
        </template>
      </template>
    </div>

    <!-- Row 1: left label = columns[2], quadrants = columns[0] + columns[1] -->
    <div class="axis-label row-label">
      <template v-if="columns[2]">
        <template v-if="editingLabel === 2">
          <div ref="editLabelRef" class="label-edit" @focusout="handleLabelFocusOut">
            <Input
              v-model="editLabelName"
              class="label-input"
              size="sm"
              @keyup.enter="saveLabel"
              @keyup.escape="editingLabel = null"
            />
            <ColorPicker v-model="editLabelColor" />
          </div>
        </template>
        <template v-else>
          <span class="label-text vertical" @click="startEditLabel(2)">
            <span class="label-dot" :style="{ background: columns[2].color }" />
            {{ columns[2].name }}
            <Pencil :size="9" class="label-edit-icon" />
          </span>
        </template>
      </template>
    </div>
    <EisenhowerQuadrant
      v-if="columns[0]"
      :title="columns[0].name"
      :column-id="columns[0].id"
      :color="columns[0].color"
      :items="itemsByColumn[columns[0].id] || []"
      :show-title="isMobile"
      @update:items="handleQuadrantUpdate(columns[0].id, $event)"
      @toggle="emit('toggle', $event)"
      @delete="emit('delete', $event)"
      @update-column="(data) => emit('updateColumn', columns[0].id, data)"
      @open-detail="emit('openDetail', $event)"
    />
    <EisenhowerQuadrant
      v-if="columns[1]"
      :title="columns[1].name"
      :column-id="columns[1].id"
      :color="columns[1].color"
      :items="itemsByColumn[columns[1].id] || []"
      :show-title="isMobile"
      @update:items="handleQuadrantUpdate(columns[1].id, $event)"
      @toggle="emit('toggle', $event)"
      @delete="emit('delete', $event)"
      @update-column="(data) => emit('updateColumn', columns[1].id, data)"
      @open-detail="emit('openDetail', $event)"
    />

    <!-- Row 2: left label = columns[3], quadrants = columns[2] + columns[3] -->
    <div class="axis-label row-label">
      <template v-if="columns[3]">
        <template v-if="editingLabel === 3">
          <div ref="editLabelRef" class="label-edit" @focusout="handleLabelFocusOut">
            <Input
              v-model="editLabelName"
              class="label-input"
              size="sm"
              @keyup.enter="saveLabel"
              @keyup.escape="editingLabel = null"
            />
            <ColorPicker v-model="editLabelColor" />
          </div>
        </template>
        <template v-else>
          <span class="label-text vertical" @click="startEditLabel(3)">
            <span class="label-dot" :style="{ background: columns[3].color }" />
            {{ columns[3].name }}
            <Pencil :size="9" class="label-edit-icon" />
          </span>
        </template>
      </template>
    </div>
    <EisenhowerQuadrant
      v-if="columns[2]"
      :title="columns[2].name"
      :column-id="columns[2].id"
      :color="columns[2].color"
      :items="itemsByColumn[columns[2].id] || []"
      :show-title="isMobile"
      @update:items="handleQuadrantUpdate(columns[2].id, $event)"
      @toggle="emit('toggle', $event)"
      @delete="emit('delete', $event)"
      @update-column="(data) => emit('updateColumn', columns[2].id, data)"
      @open-detail="emit('openDetail', $event)"
    />
    <EisenhowerQuadrant
      v-if="columns[3]"
      :title="columns[3].name"
      :column-id="columns[3].id"
      :color="columns[3].color"
      :items="itemsByColumn[columns[3].id] || []"
      :show-title="isMobile"
      @update:items="handleQuadrantUpdate(columns[3].id, $event)"
      @toggle="emit('toggle', $event)"
      @delete="emit('delete', $event)"
      @update-column="(data) => emit('updateColumn', columns[3].id, data)"
      @open-detail="emit('openDetail', $event)"
    />
  </div>
</template>

<style scoped>
.eisenhower-table {
  display: grid;
  grid-template-columns: auto 1fr 1fr;
  grid-template-rows: auto 1fr 1fr;
  gap: 12px;
  min-height: 400px;
}

.corner-cell {
  /* Empty top-left corner */
}

.axis-label {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px 8px;
}

.col-label {
  text-align: center;
}

.row-label {
  writing-mode: vertical-lr;
  transform: rotate(180deg);
  white-space: nowrap;
}

.label-text {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--app-text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: color 0.15s;
}

.label-text:hover {
  color: var(--app-text-muted);
}

.label-text.vertical {
  writing-mode: vertical-lr;
  transform: rotate(180deg);
}

.label-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.label-edit-icon {
  opacity: 0;
  transition: opacity 0.15s;
  color: var(--app-text-dim);
}

.label-text:hover .label-edit-icon {
  opacity: 1;
}

.label-edit {
  display: flex;
  flex-direction: column;
  gap: 6px;
  writing-mode: horizontal-tb;
  transform: none;
}

.row-label .label-edit {
  transform: rotate(180deg);
}

.label-input {
  max-width: 160px;
  font-size: 0.72rem;
}

@media (max-width: 768px) {
  .eisenhower-table {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    gap: 12px;
  }

  .corner-cell,
  .col-label,
  .row-label {
    display: none;
  }
}

@media (max-width: 480px) {
  .eisenhower-table {
    gap: 8px;
  }
}
</style>
