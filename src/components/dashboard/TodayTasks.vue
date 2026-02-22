<script setup lang="ts">
import { CalendarCheck } from 'lucide-vue-next'
import { Checkbox } from '@/components/ui/checkbox'
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
      Today's Tasks
    </h3>
    <div v-if="tasks.length === 0" class="empty">
      <p>No active tasks. Add some in Daily Tasks.</p>
    </div>
    <div v-else class="task-list">
      <label
        v-for="item in tasks"
        :key="item.task.id"
        class="task-item"
        :class="{ completed: item.completed }"
      >
        <Checkbox
          :checked="item.completed"
          @update:checked="emit('toggle', item.task.id)"
        />
        <span class="task-name">{{ item.task.name }}</span>
      </label>
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
  text-decoration: line-through;
  color: var(--app-text-muted);
}
</style>
