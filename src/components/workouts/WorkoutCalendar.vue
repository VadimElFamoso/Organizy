<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import type { WorkoutCalendarDay } from '@/services/api'

const props = defineProps<{
  days: WorkoutCalendarDay[]
}>()

const emit = defineEmits<{
  monthChange: [year: number, month: number]
  dayClick: [date: string]
}>()

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)

const monthNames = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

const dayNames = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

function prevMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  emit('monthChange', currentYear.value, currentMonth.value)
}

function nextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  emit('monthChange', currentYear.value, currentMonth.value)
}

function getDaysInMonth() {
  return new Date(currentYear.value, currentMonth.value, 0).getDate()
}

function getFirstDayOfWeek() {
  const day = new Date(currentYear.value, currentMonth.value - 1, 1).getDay()
  // Convert to Monday-start (0=Mon, 6=Sun)
  return (day + 6) % 7
}

function hasWorkout(day: number): boolean {
  const dateStr = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  return props.days.some(d => d.date === dateStr)
}

function isToday(day: number): boolean {
  const now = new Date()
  return day === now.getDate() && currentMonth.value === now.getMonth() + 1 && currentYear.value === now.getFullYear()
}

function handleDayClick(day: number) {
  const dateStr = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  emit('dayClick', dateStr)
}

onMounted(() => {
  emit('monthChange', currentYear.value, currentMonth.value)
})
</script>

<template>
  <div class="workout-calendar">
    <div class="cal-header">
      <Button variant="ghost" size="sm" @click="prevMonth">
        <ChevronLeft :size="16" />
      </Button>
      <span class="cal-title">{{ monthNames[currentMonth - 1] }} {{ currentYear }}</span>
      <Button variant="ghost" size="sm" @click="nextMonth">
        <ChevronRight :size="16" />
      </Button>
    </div>

    <div class="cal-grid">
      <div v-for="name in dayNames" :key="name" class="cal-day-name">{{ name }}</div>
      <div v-for="_ in getFirstDayOfWeek()" :key="'empty-' + _" class="cal-empty" />
      <div
        v-for="day in getDaysInMonth()"
        :key="day"
        class="cal-day"
        :class="{ today: isToday(day), 'has-workout': hasWorkout(day) }"
        @click="handleDayClick(day)"
      >
        <span>{{ day }}</span>
        <div v-if="hasWorkout(day)" class="workout-dot" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.workout-calendar {
  background: var(--app-surface, #fff);
  border: 1px solid var(--app-border, #e2ddd5);
  border-radius: 12px;
  padding: 20px;
}

.cal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.cal-title {
  font-weight: 600;
  font-size: 0.9rem;
  letter-spacing: -0.01em;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.cal-day-name {
  text-align: center;
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--app-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 4px 0;
}

.cal-empty {
  aspect-ratio: 1;
}

.cal-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  position: relative;
  transition: background 0.15s;
}

.cal-day:hover {
  background: var(--app-surface-2);
}

.cal-day.today {
  font-weight: 700;
  border: 1px solid var(--app-border-hover);
}

.cal-day.has-workout {
  background: rgba(22, 163, 74, 0.1);
}

.workout-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #16a34a;
  position: absolute;
  bottom: 4px;
}
</style>
