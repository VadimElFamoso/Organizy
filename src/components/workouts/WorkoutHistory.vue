<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Pencil, Trash2, Clock, Dumbbell } from 'lucide-vue-next'
import type { WorkoutItem } from '@/services/api'

defineProps<{
  workouts: WorkoutItem[]
}>()

const emit = defineEmits<{
  edit: [id: string]
  delete: [id: string]
}>()
</script>

<template>
  <div class="workout-history">
    <div v-if="workouts.length === 0" class="empty">
      <p>No workouts logged yet.</p>
    </div>
    <div v-else class="history-list">
      <div v-for="w in workouts" :key="w.id" class="history-item">
        <div class="item-left">
          <Dumbbell :size="16" class="item-icon" />
          <div class="item-info">
            <span class="item-type">{{ w.workout_type }}</span>
            <span class="item-date">{{ w.workout_date }}</span>
          </div>
        </div>
        <div class="item-right">
          <span v-if="w.duration_minutes" class="item-duration">
            <Clock :size="12" />
            {{ w.duration_minutes }}m
          </span>
          <Button variant="ghost" size="sm" @click="emit('edit', w.id)">
            <Pencil :size="14" />
          </Button>
          <Button variant="ghost" size="sm" @click="emit('delete', w.id)">
            <Trash2 :size="14" />
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workout-history {
  background: var(--app-surface, #fff);
  border: 1px solid var(--app-border, #e2ddd5);
  border-radius: 12px;
  padding: 20px;
}

.empty {
  text-align: center;
  color: var(--app-text-muted);
  padding: 24px 0;
}

.empty p {
  margin: 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  transition: background 0.15s;
}

.history-item:hover {
  background: var(--app-surface-2);
}

.item-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-icon {
  color: var(--theme-accent);
  flex-shrink: 0;
}

.item-info {
  display: flex;
  flex-direction: column;
}

.item-type {
  font-weight: 500;
  font-size: 0.9rem;
}

.item-date {
  font-size: 0.75rem;
  color: var(--app-text-muted);
}

.item-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.item-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: var(--app-text-muted);
  margin-right: 4px;
}
</style>
