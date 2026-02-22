<script setup lang="ts">
import { Checkbox } from '@/components/ui/checkbox'
import { Button } from '@/components/ui/button'
import { Trash2 } from 'lucide-vue-next'
import type { TodoItem } from '@/services/api'

defineProps<{
  todo: TodoItem
}>()

const emit = defineEmits<{
  toggle: [id: string]
  delete: [id: string]
}>()
</script>

<template>
  <div class="kanban-card">
    <div class="card-top">
      <Checkbox
        :checked="todo.is_done"
        @update:checked="emit('toggle', todo.id)"
      />
      <span class="card-title">{{ todo.title }}</span>
    </div>
    <p v-if="todo.description" class="card-desc">{{ todo.description }}</p>
    <div class="card-actions">
      <Button variant="ghost" size="sm" @click="emit('delete', todo.id)">
        <Trash2 :size="12" />
      </Button>
    </div>
  </div>
</template>

<style scoped>
.kanban-card {
  background: var(--app-surface, #fff);
  border: 1px solid var(--app-border, #e2ddd5);
  border-radius: 8px;
  padding: 12px;
  cursor: grab;
  transition: box-shadow 0.15s;
}

.kanban-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-top {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.card-title {
  font-size: 0.85rem;
  font-weight: 500;
  flex: 1;
  word-break: break-word;
}

.card-desc {
  font-size: 0.75rem;
  color: var(--app-text-muted);
  margin: 6px 0 0 26px;
  line-height: 1.4;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
  opacity: 0;
  transition: opacity 0.15s;
}

.kanban-card:hover .card-actions {
  opacity: 1;
}
</style>
