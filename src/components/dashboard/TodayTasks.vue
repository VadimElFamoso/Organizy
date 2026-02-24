<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { CalendarCheck, Check, ArrowRight } from 'lucide-vue-next'
import type { TodayTaskItem } from '@/services/api'

const MAX_SHOWN = 5

const props = defineProps<{
  tasks: TodayTaskItem[]
}>()

const emit = defineEmits<{
  toggle: [taskId: string]
}>()

const visibleTasks = computed(() => props.tasks.slice(0, MAX_SHOWN))
const hiddenCount = computed(() => Math.max(0, props.tasks.length - MAX_SHOWN))
const doneCount = computed(() => props.tasks.filter(t => t.completed).length)
const totalCount = computed(() => props.tasks.length)
const progressPct = computed(() => totalCount.value === 0 ? 0 : Math.round((doneCount.value / totalCount.value) * 100))
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
    <template v-else>
      <div class="task-list">
        <div
          v-for="item in visibleTasks"
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
      <div class="footer">
        <div class="progress-bar">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: progressPct + '%' }" />
          </div>
          <span class="progress-label">{{ doneCount }}/{{ totalCount }}</span>
        </div>
        <RouterLink v-if="hiddenCount > 0" to="/daily-tasks" class="more-link">
          +{{ hiddenCount }} de plus
          <ArrowRight :size="11" />
        </RouterLink>
      </div>
    </template>
  </div>
</template>

<style scoped>
.today-tasks {
  background: var(--app-surface, #fff);
  border: 1px solid var(--app-border, #e2ddd5);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 0;
  color: var(--app-text-dim);
}

.empty {
  color: var(--app-text-muted);
  font-size: 0.875rem;
  text-align: center;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty p {
  margin: 0;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  justify-content: center;
  padding: 12px 0;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  min-width: 0;
}

.task-item:hover {
  background: var(--app-surface-2);
}

.task-name {
  font-size: 0.88rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.task-item.completed .task-name {
  color: var(--app-text-muted);
  text-decoration: line-through;
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

.footer {
  border-top: 1px solid var(--app-border);
  padding-top: 12px;
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-track {
  flex: 1;
  height: 4px;
  background: var(--app-surface-3);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--app-text);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-label {
  font-size: 0.72rem;
  color: var(--app-text-dim);
  font-weight: 500;
  white-space: nowrap;
}

.more-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  font-weight: 500;
  color: var(--app-text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.more-link:hover {
  color: var(--app-text);
}
</style>
