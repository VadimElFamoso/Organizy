<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Pencil, Trash2, Clock, Dumbbell, ChevronDown, ChevronRight } from 'lucide-vue-next'
import type { WorkoutItem } from '@/services/api'

defineProps<{
  workouts: WorkoutItem[]
}>()

const emit = defineEmits<{
  edit: [id: string]
  delete: [id: string]
}>()

const expandedIds = ref<Set<string>>(new Set())

function toggleExpand(id: string) {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
}

function formatDuration(minutes: number): string {
  if (minutes >= 60) {
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    return m > 0 ? `${h}h${String(m).padStart(2, '0')}` : `${h}h`
  }
  return `${minutes}m`
}
</script>

<template>
  <div class="workout-history">
    <div v-if="workouts.length === 0" class="empty">
      <p>Aucune séance enregistrée.</p>
    </div>
    <div v-else class="history-list">
      <div v-for="w in workouts" :key="w.id" class="history-item-wrapper">
        <div class="history-item" @click="w.exercises.length > 0 && toggleExpand(w.id)">
          <div class="item-left">
            <Dumbbell :size="16" class="item-icon" />
            <div class="item-info">
              <span class="item-type">{{ w.workout_type }}</span>
              <span class="item-date">{{ w.workout_date }}</span>
            </div>
          </div>
          <div class="item-right">
            <span v-if="w.exercises.length > 0" class="item-exercise-count">
              {{ w.exercises.length }} ex.
            </span>
            <span v-if="w.duration_minutes" class="item-duration">
              <Clock :size="12" />
              {{ formatDuration(w.duration_minutes) }}
            </span>
            <component
              v-if="w.exercises.length > 0"
              :is="expandedIds.has(w.id) ? ChevronDown : ChevronRight"
              :size="14"
              class="expand-icon"
            />
            <Button variant="ghost" size="sm" @click.stop="emit('edit', w.id)">
              <Pencil :size="14" />
            </Button>
            <Button variant="ghost" size="sm" @click.stop="emit('delete', w.id)">
              <Trash2 :size="14" />
            </Button>
          </div>
        </div>
        <!-- Expanded exercises -->
        <div v-if="expandedIds.has(w.id) && w.exercises.length > 0" class="exercise-list">
          <div v-for="ex in w.exercises" :key="ex.id || ex.sort_order" class="exercise-item">
            <span class="exercise-name">{{ ex.name }}</span>
            <span v-if="ex.notes" class="exercise-notes">{{ ex.notes }}</span>
          </div>
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
  max-height: 500px;
  overflow-y: auto;
}

.history-item-wrapper {
  border-radius: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  transition: background 0.15s, box-shadow 0.15s;
  cursor: default;
}

.history-item:hover {
  background: var(--app-surface-2);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.item-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex: 1;
}

.item-icon {
  color: var(--theme-accent);
  flex-shrink: 0;
}

.item-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
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
  gap: 8px;
  flex-shrink: 0;
  white-space: nowrap;
  margin-left: 20px;
}

.item-exercise-count {
  font-size: 0.72rem;
  color: var(--app-text-dim);
  background: var(--app-surface-3);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
  white-space: nowrap;
}

.item-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: var(--app-text-muted);
  white-space: nowrap;
}

.expand-icon {
  color: var(--app-text-muted);
  cursor: pointer;
}

/* Expanded exercise list */
.exercise-list {
  padding: 4px 12px 10px 38px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.exercise-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 4px 8px;
  background: var(--app-surface-2);
  border-radius: 6px;
  min-width: 0;
}

.exercise-name {
  font-size: 0.82rem;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.exercise-notes {
  font-size: 0.75rem;
  color: var(--app-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}
</style>
