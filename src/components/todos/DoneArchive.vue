<script setup lang="ts">
import { ref } from 'vue'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Archive, Trash2 } from 'lucide-vue-next'
import type { TodoItem } from '@/services/api'

defineProps<{
  todos: TodoItem[]
}>()

const emit = defineEmits<{
  bulkDelete: [ids: string[]]
  undone: [id: string]
}>()

const selectedIds = ref<Set<string>>(new Set())

function toggleSelect(id: string) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
}

function toggleAll(todos: TodoItem[]) {
  if (selectedIds.value.size === todos.length) {
    selectedIds.value.clear()
  } else {
    selectedIds.value = new Set(todos.map(t => t.id))
  }
}

function handleBulkDelete() {
  emit('bulkDelete', Array.from(selectedIds.value))
  selectedIds.value.clear()
}

</script>

<template>
  <Sheet>
    <SheetTrigger as-child>
      <Button variant="outline" size="sm">
        <Archive :size="14" />
        Done ({{ todos.length }})
      </Button>
    </SheetTrigger>
    <SheetContent>
      <SheetHeader>
        <SheetTitle>Done Archive</SheetTitle>
        <SheetDescription>Completed todos. Select items to delete them permanently.</SheetDescription>
      </SheetHeader>

      <div class="archive-actions">
        <Button
          v-if="selectedIds.size > 0"
          variant="destructive"
          size="sm"
          @click="handleBulkDelete"
        >
          <Trash2 :size="14" />
          Delete {{ selectedIds.size }} selected
        </Button>
        <Button
          v-if="todos.length > 0"
          variant="ghost"
          size="sm"
          @click="toggleAll(todos)"
        >
          {{ selectedIds.size === todos.length ? 'Deselect all' : 'Select all' }}
        </Button>
      </div>

      <div v-if="todos.length === 0" class="empty">
        <p>No completed todos yet.</p>
      </div>

      <div v-else class="archive-list">
        <div v-for="todo in todos" :key="todo.id" class="archive-item">
          <Checkbox
            :checked="selectedIds.has(todo.id)"
            @update:checked="toggleSelect(todo.id)"
          />
          <div class="item-info">
            <span class="item-title">{{ todo.title }}</span>
            <span v-if="todo.done_at" class="item-date">
              Done {{ new Date(todo.done_at).toLocaleDateString() }}
            </span>
          </div>
        </div>
      </div>
    </SheetContent>
  </Sheet>
</template>

<style scoped>
.archive-actions {
  display: flex;
  gap: 8px;
  padding: 12px 0;
  border-bottom: 1px solid var(--app-border);
  margin-bottom: 12px;
}

.empty {
  text-align: center;
  color: var(--app-text-muted);
  padding: 32px 0;
}

.empty p {
  margin: 0;
}

.archive-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: calc(100vh - 250px);
  overflow-y: auto;
}

.archive-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-radius: 6px;
  transition: background 0.15s;
}

.archive-item:hover {
  background: var(--app-surface-2);
}

.item-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.item-title {
  font-size: 0.85rem;
  text-decoration: line-through;
  color: var(--app-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-date {
  font-size: 0.7rem;
  color: var(--app-text-dim);
}
</style>
