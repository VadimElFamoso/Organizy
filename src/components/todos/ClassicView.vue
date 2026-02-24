<script setup lang="ts">
import { ref, computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowUpDown } from 'lucide-vue-next'
import ClassicRow from './ClassicRow.vue'
import type { TaskItem } from '@/services/api'

const props = defineProps<{
  items: TaskItem[]
}>()

const emit = defineEmits<{
  toggle: [id: string]
  delete: [id: string]
  openDetail: [task: TaskItem]
}>()

type SortField = 'priority' | 'due_date' | 'created_at'
const sortField = ref<SortField>('priority')
const sortAsc = ref(true)

const priorityOrder: Record<string, number> = {
  urgent: 0,
  high: 1,
  medium: 2,
  low: 3,
}

const sortedItems = computed(() => {
  const copy = [...props.items]
  const dir = sortAsc.value ? 1 : -1

  copy.sort((a, b) => {
    if (sortField.value === 'priority') {
      const pa = a.priority ? (priorityOrder[a.priority] ?? 4) : 4
      const pb = b.priority ? (priorityOrder[b.priority] ?? 4) : 4
      return (pa - pb) * dir
    }
    if (sortField.value === 'due_date') {
      const da = a.due_date || '9999-12-31'
      const db = b.due_date || '9999-12-31'
      return da.localeCompare(db) * dir
    }
    // created_at
    return a.created_at.localeCompare(b.created_at) * dir
  })

  return copy
})

const sortOptions: { field: SortField; label: string }[] = [
  { field: 'priority', label: 'Priorité' },
  { field: 'due_date', label: 'Échéance' },
  { field: 'created_at', label: 'Date de création' },
]

function toggleSort(field: SortField) {
  if (sortField.value === field) {
    sortAsc.value = !sortAsc.value
  } else {
    sortField.value = field
    sortAsc.value = true
  }
}
</script>

<template>
  <div class="classic-view">
    <div class="sort-bar">
      <span class="sort-label">Trier par :</span>
      <Button
        v-for="opt in sortOptions"
        :key="opt.field"
        variant="ghost"
        size="sm"
        class="sort-btn"
        :class="{ active: sortField === opt.field }"
        @click="toggleSort(opt.field)"
      >
        {{ opt.label }}
        <ArrowUpDown v-if="sortField === opt.field" :size="12" />
      </Button>
    </div>

    <div v-if="sortedItems.length === 0" class="empty">
      <p>Aucune tâche active.</p>
    </div>

    <div v-else class="task-list">
      <ClassicRow
        v-for="item in sortedItems"
        :key="item.id"
        :task="item"
        @toggle="emit('toggle', $event)"
        @delete="emit('delete', $event)"
        @open-detail="emit('openDetail', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.classic-view {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 700px;
  margin: 0 auto;
}

.sort-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 0;
}

.sort-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--app-text-dim);
  margin-right: 4px;
}

.sort-btn {
  font-size: 0.78rem;
  gap: 4px;
}

.sort-btn.active {
  color: var(--app-text);
  font-weight: 600;
}

.empty {
  text-align: center;
  color: var(--app-text-muted);
  padding: 48px 0;
}

.empty p {
  margin: 0;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
</style>
