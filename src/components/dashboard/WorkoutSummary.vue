<script setup lang="ts">
import { Dumbbell, Flame, Clock, ChevronDown } from 'lucide-vue-next'
import { ref } from 'vue'
import type { WorkoutSummary } from '@/services/api'

defineProps<{
  summary: WorkoutSummary | null
}>()

const expandedId = ref<string | null>(null)

function toggleExpand(id: string) {
  expandedId.value = expandedId.value === id ? null : id
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
  <div class="workout-summary">
    <h3 class="section-title">
      <Dumbbell :size="18" />
      Sport
    </h3>

    <div v-if="!summary || summary.total_workouts === 0" class="empty">
      <p>Aucune séance enregistrée.</p>
    </div>

    <template v-else>
      <!-- Compact stats row -->
      <div class="stats-row">
        <div class="stat-pill">
          <Dumbbell :size="13" class="stat-pill-icon" />
          <span class="stat-pill-value">{{ summary.total_workouts }}</span>
          <span class="stat-pill-label">séances</span>
        </div>
        <div class="stat-pill">
          <Flame :size="13" class="stat-pill-icon" />
          <span class="stat-pill-value">{{ summary.current_streak }}</span>
          <span class="stat-pill-label">j. consécutifs</span>
        </div>
      </div>

      <!-- Today's workouts -->
      <div class="today-section">
        <div class="today-label">Aujourd'hui</div>
        <div v-if="summary.today_workouts.length === 0" class="today-empty">
          Pas encore de séance aujourd'hui.
        </div>
        <div v-else class="today-list">
          <div v-for="w in summary.today_workouts" :key="w.id" class="today-session">
            <div class="today-session-header" @click="w.exercises.length > 0 && toggleExpand(w.id)">
              <span class="today-session-type">{{ w.workout_type }}</span>
              <div class="today-session-right">
                <span v-if="w.exercises.length > 0" class="today-session-count">
                  {{ w.exercises.length }} ex.
                </span>
                <span v-if="w.duration_minutes" class="today-session-duration">
                  <Clock :size="11" />
                  {{ formatDuration(w.duration_minutes) }}
                </span>
                <ChevronDown
                  v-if="w.exercises.length > 0"
                  :size="13"
                  class="today-session-chevron"
                  :class="{ rotated: expandedId === w.id }"
                />
              </div>
            </div>
            <div v-if="expandedId === w.id && w.exercises.length > 0" class="today-session-body">
              <div v-for="ex in w.exercises" :key="ex.id || ex.sort_order" class="today-exercise">
                <span class="today-exercise-name">{{ ex.name }}</span>
                <span v-if="ex.notes" class="today-exercise-notes">{{ ex.notes }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.workout-summary {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 0 0 14px;
  color: var(--app-text-dim);
}

.empty {
  color: var(--app-text-muted);
  font-size: 0.875rem;
  text-align: center;
  padding: 16px 0;
}

.empty p {
  margin: 0;
}

/* Compact stat pills */
.stats-row {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}

.stat-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background: var(--app-surface-2);
  border-radius: 6px;
}

.stat-pill-icon {
  color: var(--theme-accent);
  flex-shrink: 0;
}

.stat-pill-value {
  font-weight: 700;
  font-size: 0.82rem;
}

.stat-pill-label {
  font-size: 0.68rem;
  color: var(--app-text-dim);
  font-weight: 500;
}

/* Today section */
.today-section {
  border-top: 1px solid var(--app-border);
  padding-top: 12px;
}

.today-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--app-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.today-empty {
  color: var(--app-text-muted);
  font-size: 0.82rem;
  padding: 8px 0;
}

.today-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.today-session {
  background: var(--app-surface-2);
  border-radius: 8px;
  padding: 10px 12px;
}

.today-session-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}

.today-session-type {
  font-weight: 600;
  font-size: 0.85rem;
}

.today-session-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  margin-left: 12px;
}

.today-session-count {
  font-size: 0.68rem;
  color: var(--app-text-dim);
  background: var(--app-surface-3);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
  white-space: nowrap;
}

.today-session-duration {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 0.75rem;
  color: var(--app-text-muted);
  white-space: nowrap;
}

.today-session-chevron {
  color: var(--app-text-dim);
  transition: transform 0.15s ease;
}

.today-session-chevron.rotated {
  transform: rotate(180deg);
}

.today-session-body {
  padding-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.today-exercise {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 4px 0;
  border-top: 1px solid var(--app-border);
}

.today-exercise-name {
  font-size: 0.78rem;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.today-exercise-notes {
  font-size: 0.72rem;
  color: var(--app-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}
</style>
