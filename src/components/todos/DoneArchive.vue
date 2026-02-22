<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Archive, Trash2, Check } from 'lucide-vue-next'
import type { TodoItem } from '@/services/api'

const props = defineProps<{
  todos: TodoItem[]
}>()

const emit = defineEmits<{
  bulkDelete: [ids: string[]]
  delete: [id: string]
}>()

const selectedIds = ref<Set<string>>(new Set())

const allSelected = computed(() =>
  props.todos.length > 0 && selectedIds.value.size === props.todos.length
)

function toggleSelect(id: string) {
  const next = new Set(selectedIds.value)
  if (next.has(id)) {
    next.delete(id)
  } else {
    next.add(id)
  }
  selectedIds.value = next
}

function toggleAll() {
  if (allSelected.value) {
    selectedIds.value = new Set()
  } else {
    selectedIds.value = new Set(props.todos.map(t => t.id))
  }
}

function handleBulkDelete() {
  emit('bulkDelete', Array.from(selectedIds.value))
  selectedIds.value = new Set()
}

function handleDelete(id: string) {
  selectedIds.value.delete(id)
  emit('delete', id)
}
</script>

<template>
  <Sheet>
    <SheetTrigger as-child>
      <Button variant="outline" size="sm">
        <Archive :size="14" />
        Terminées ({{ todos.length }})
      </Button>
    </SheetTrigger>
    <SheetContent>
      <SheetHeader>
        <SheetTitle>Archive des tâches terminées</SheetTitle>
        <SheetDescription>Tâches complétées. Sélectionnez des éléments pour les supprimer définitivement.</SheetDescription>
      </SheetHeader>

      <div v-if="todos.length > 0" class="archive-actions">
        <Button
          variant="ghost"
          size="sm"
          @click="toggleAll"
        >
          {{ allSelected ? 'Tout désélectionner' : 'Tout sélectionner' }}
        </Button>
        <Button
          v-if="selectedIds.size > 0"
          variant="destructive"
          size="sm"
          @click="handleBulkDelete"
        >
          <Trash2 :size="14" />
          Supprimer ({{ selectedIds.size }})
        </Button>
      </div>

      <div v-if="todos.length === 0" class="empty">
        <p>Aucune tâche terminée pour le moment.</p>
      </div>

      <div v-else class="archive-list">
        <div
          v-for="todo in todos"
          :key="todo.id"
          class="archive-item"
          :class="{ selected: selectedIds.has(todo.id) }"
          @click="toggleSelect(todo.id)"
        >
          <div class="square" :class="{ filled: selectedIds.has(todo.id) }">
            <Check v-if="selectedIds.has(todo.id)" :size="12" class="check-icon" />
          </div>
          <div class="item-info">
            <span class="item-title">{{ todo.title }}</span>
            <span v-if="todo.done_at" class="item-date">
              Terminée le {{ new Date(todo.done_at).toLocaleDateString('fr-FR') }}
            </span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            class="item-delete"
            @click.stop="handleDelete(todo.id)"
          >
            <Trash2 :size="13" />
          </Button>
        </div>
      </div>
    </SheetContent>
  </Sheet>
</template>

<style scoped>
.archive-actions {
  display: flex;
  align-items: center;
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
  gap: 2px;
  max-height: calc(100vh - 250px);
  overflow-y: auto;
}

.archive-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.archive-item:hover {
  background: var(--app-surface-2);
}

.archive-item.selected {
  background: var(--app-surface-2);
}

.square {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  flex-shrink: 0;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.square.filled {
  background: var(--app-text);
  border-color: var(--app-text);
}

.check-icon {
  color: var(--app-surface);
}

.item-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.item-title {
  font-size: 0.85rem;
  color: var(--app-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-date {
  font-size: 0.7rem;
  color: var(--app-text-dim);
}

.item-delete {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
  padding: 4px;
  height: auto;
  color: var(--app-text-dim);
}

.archive-item:hover .item-delete {
  opacity: 1;
}
</style>
