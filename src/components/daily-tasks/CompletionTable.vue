<script setup lang="ts">
import { computed } from 'vue'
import type { DailyTask, Completion } from '@/services/api'

const props = defineProps<{
  tasks: DailyTask[]
  completions: Completion[]
  weekDates: string[]
}>()

const dayLabels = computed(() =>
  props.weekDates.map(d => {
    const date = new Date(d)
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    return { date: d, label: days[date.getDay()], day: date.getDate() }
  })
)

const completionSet = computed(() => {
  const set = new Set<string>()
  for (const c of props.completions) {
    set.add(`${c.task_id}:${c.completed_date}`)
  }
  return set
})

function isCompleted(taskId: string, date: string): boolean {
  return completionSet.value.has(`${taskId}:${date}`)
}

const emit = defineEmits<{
  toggle: [taskId: string, date: string]
}>()
</script>

<template>
  <div class="completion-table-wrapper">
    <table class="completion-table">
      <thead>
        <tr>
          <th class="task-col">Task</th>
          <th v-for="d in dayLabels" :key="d.date" class="day-col">
            <span class="day-name">{{ d.label }}</span>
            <span class="day-num">{{ d.day }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in tasks" :key="task.id">
          <td class="task-name">{{ task.name }}</td>
          <td
            v-for="d in dayLabels"
            :key="d.date"
            class="cell"
            @click="emit('toggle', task.id, d.date)"
          >
            <div
              class="square"
              :class="{ filled: isCompleted(task.id, d.date) }"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.completion-table-wrapper {
  overflow-x: auto;
}

.completion-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.completion-table th,
.completion-table td {
  padding: 8px;
  text-align: center;
}

.task-col {
  text-align: left;
  font-weight: 500;
  color: var(--app-text-muted);
  min-width: 120px;
}

.day-col {
  width: 48px;
  font-weight: 400;
}

.day-name {
  display: block;
  font-size: 0.7rem;
  color: var(--app-text-muted);
}

.day-num {
  display: block;
  font-size: 0.8rem;
  font-weight: 500;
}

.task-name {
  text-align: left;
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell {
  cursor: pointer;
}

.square {
  width: 20px;
  height: 20px;
  border-radius: 3px;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  margin: 0 auto;
  transition: all 0.15s;
}

.square.filled {
  background: #16a34a;
  border-color: #16a34a;
}

.cell:hover .square:not(.filled) {
  border-color: var(--app-border-hover);
  background: var(--app-surface-3);
}
</style>
