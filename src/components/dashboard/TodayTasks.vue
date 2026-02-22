<script setup lang="ts">
import { CalendarCheck, Check } from 'lucide-vue-next'
import type { TodayTaskItem } from '@/services/api'

defineProps<{
  tasks: TodayTaskItem[]
}>()

const emit = defineEmits<{
  toggle: [taskId: string]
}>()
</script>

<template>
  <div class="today-tasks">
    <h3 class="section-title">
      <CalendarCheck :size="18" />
      Tâches du jour
    </h3>
    <div v-if="tasks.length === 0" class="empty">
      <p>Aucune tâche active. Ajoutez-en dans Tâches quotidiennes.</p>
    </div>
    <div v-else class="task-list">
      <div
        v-for="item in tasks"
        :key="item.task.id"
        class="task-item"
        :class="{ completed: item.completed }"
        @click="emit('toggle', item.task.id)"
      >
        <div class="square" :class="{ filled: item.completed }">
          <Check v-if="item.completed" :size="14" class="check-icon" />
        </div>
        <span class="task-name">{{ item.task.name }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.today-tasks {
  background: var(--app-surface, #fff);
  border: 1px solid var(--app-border, #e2ddd5);
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
  margin: 0 0 16px;
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

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.task-item:hover {
  background: var(--app-surface-2);
}

.task-name {
  font-size: 0.9rem;
}

.task-item.completed .task-name {
  color: var(--app-text-muted);
}

.square {
  width: 18px;
  height: 18px;
  border-radius: 4px;
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

.task-item:hover .square:not(.filled) {
  border-color: var(--app-border-hover);
  background: var(--app-surface-3);
}
</style>
