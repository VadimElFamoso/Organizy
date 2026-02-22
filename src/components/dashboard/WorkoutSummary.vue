<script setup lang="ts">
import { Dumbbell, Flame, Calendar } from 'lucide-vue-next'
import type { WorkoutSummary } from '@/services/api'

defineProps<{
  summary: WorkoutSummary | null
}>()
</script>

<template>
  <div class="workout-summary">
    <h3 class="section-title">
      <Dumbbell :size="18" />
      Workout Summary
    </h3>
    <div v-if="!summary || summary.total_workouts === 0" class="empty">
      <p>No workouts yet. Start logging!</p>
    </div>
    <div v-else class="stats">
      <div class="stat">
        <Dumbbell :size="16" class="stat-icon" />
        <div class="stat-info">
          <span class="stat-value">{{ summary.total_workouts }}</span>
          <span class="stat-label">Total</span>
        </div>
      </div>
      <div class="stat">
        <Flame :size="16" class="stat-icon" />
        <div class="stat-info">
          <span class="stat-value">{{ summary.current_streak }}</span>
          <span class="stat-label">Day streak</span>
        </div>
      </div>
      <div v-if="summary.last_workout" class="stat">
        <Calendar :size="16" class="stat-icon" />
        <div class="stat-info">
          <span class="stat-value">{{ summary.last_workout.workout_type }}</span>
          <span class="stat-label">{{ summary.last_workout.workout_date }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workout-summary {
  background: var(--app-surface, #fff);
  border: 1px solid var(--app-border, #e2ddd5);
  border-radius: 12px;
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 16px;
  color: var(--app-text);
}

.section-title svg {
  color: var(--theme-accent);
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

.stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--app-surface-2);
  border-radius: 8px;
}

.stat-icon {
  color: var(--theme-accent);
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-weight: 600;
  font-size: 0.9rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--app-text-muted);
}
</style>
