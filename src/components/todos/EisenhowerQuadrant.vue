<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Pencil } from 'lucide-vue-next'
import TaskCard from './TaskCard.vue'
import ColorPicker from './ColorPicker.vue'
import type { TaskItem } from '@/services/api'

const props = withDefaults(defineProps<{
  title: string
  columnId: string
  color: string
  items: TaskItem[]
  showTitle?: boolean
}>(), {
  showTitle: true,
})

const emit = defineEmits<{
  'update:items': [items: TaskItem[]]
  toggle: [id: string]
  delete: [id: string]
  updateColumn: [data: { name?: string; color?: string }]
  openDetail: [task: TaskItem]
}>()

const isEditingName = ref(false)
const editName = ref('')
const editColor = ref('')

function startEdit() {
  editName.value = props.title
  editColor.value = props.color
  isEditingName.value = true
}

function saveName() {
  const data: { name?: string; color?: string } = {}
  if (editName.value.trim() && editName.value.trim() !== props.title) {
    data.name = editName.value.trim()
  }
  if (editColor.value && editColor.value !== props.color) {
    data.color = editColor.value
  }
  if (Object.keys(data).length > 0) {
    emit('updateColumn', data)
  }
  isEditingName.value = false
}

const editGroupRef = ref<HTMLElement | null>(null)

function handleEditFocusOut(e: FocusEvent) {
  const related = e.relatedTarget as Node | null
  if (editGroupRef.value && related && editGroupRef.value.contains(related)) return
  saveName()
}

function onUpdate(items: TaskItem[]) {
  emit('update:items', items)
}
</script>

<template>
  <div class="quadrant">
    <div v-if="showTitle" class="quadrant-header">
      <div class="header-left">
        <div class="color-dot" :style="{ background: color }" />
        <template v-if="isEditingName">
          <div ref="editGroupRef" class="edit-group" @focusout="handleEditFocusOut">
            <Input
              v-model="editName"
              class="name-input"
              size="sm"
              @keyup.enter="saveName"
              @keyup.escape="isEditingName = false"
            />
            <ColorPicker v-model="editColor" />
            <Button size="sm" tabindex="0" @click="saveName">OK</Button>
          </div>
        </template>
        <template v-else>
          <span class="quadrant-title" @click="startEdit">
            {{ title }}
            <Pencil :size="10" class="edit-icon" />
          </span>
        </template>
        <span v-if="!isEditingName" class="quadrant-count">{{ items.length }}</span>
      </div>
    </div>
    <div v-else class="quadrant-header-minimal">
      <span class="quadrant-count">{{ items.length }}</span>
    </div>

    <VueDraggable
      :model-value="items"
      @update:model-value="onUpdate"
      group="eisenhower"
      class="quadrant-content"
      item-key="id"
      :animation="150"
      ghost-class="ghost"
    >
      <TaskCard
        v-for="task in items"
        :key="task.id"
        :task="task"
        @toggle="emit('toggle', $event)"
        @delete="emit('delete', $event)"
        @open-detail="emit('openDetail', $event)"
      />
    </VueDraggable>
  </div>
</template>

<style scoped>
.quadrant {
  background: var(--app-surface-2, #f5f2ed);
  border-radius: 12px;
  padding: 12px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
}

.quadrant-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 0 4px;
}

.quadrant-header-minimal {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
  padding: 0 4px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.edit-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.quadrant-title {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--app-text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.edit-icon {
  opacity: 0;
  transition: opacity 0.15s;
  color: var(--app-text-dim);
}

.quadrant-title:hover .edit-icon {
  opacity: 1;
}

.name-input {
  max-width: 180px;
  font-size: 0.72rem;
}

.quadrant-count {
  font-size: 0.65rem;
  color: var(--app-text-muted);
  background: var(--app-surface-3);
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 500;
}

.quadrant-content {
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
