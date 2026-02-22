<script setup lang="ts">
import { computed } from 'vue'
import type { DailyTask, Completion } from '@/services/api'

const props = defineProps<{
  tasks: DailyTask[]
  completions: Completion[]
  weekDates: string[]
  today: string
}>()

const dayLabels = computed(() =>
  props.weekDates.map(d => {
    const date = new Date(d)
    const days = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']
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

function isToday(date: string): boolean {
  return date === props.today
}

function handleClick(taskId: string, date: string) {
  if (isToday(date)) {
    emit('toggle', taskId, date)
  }
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
          <th class="task-col">Tâche</th>
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
            :class="{ disabled: !isToday(d.date) }"
            @click="handleClick(task.id, d.date)"
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
  table-layout: fixed;
  font-size: 0.85rem;
}

.completion-table th,
.completion-table td {
  padding: 8px;
  text-align: center;
}

.completion-table th.task-col {
  padding-left: 48px;
  text-align: left;
}

.completion-table td.task-name {
  padding-left: 48px;
  text-align: left;
}

.task-col {
  text-align: left;
  font-weight: 600;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--app-text-dim);
  width: 160px;
  min-width: 160px;
  max-width: 160px;
  padding-left: 0;
}

.day-col {
  width: 48px;
  font-weight: 400;
}

.day-name {
  display: block;
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--app-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.day-num {
  display: block;
  font-size: 0.8rem;
  font-weight: 500;
}

.task-name {
  text-align: left;
  font-weight: 500;
  width: 160px;
  min-width: 160px;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-left: 0;
}

.cell {
  cursor: pointer;
}

.cell.disabled {
  cursor: default;
  opacity: 0.5;
}

.square {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  margin: 0 auto;
  transition: all 0.15s;
}

.square.filled {
  background: var(--app-text);
  border-color: var(--app-text);
}

.cell:not(.disabled):hover .square:not(.filled) {
  border-color: var(--app-border-hover);
  background: var(--app-surface-3);
}
</style>
