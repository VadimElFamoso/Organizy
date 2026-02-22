<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  year: number
}>()

const today = new Date()
const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

const isLeapYear = computed(() => {
  const y = props.year
  return y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0)
})

const daysInYear = computed(() => (isLeapYear.value ? 366 : 365))

const days = computed(() => {
  const result: { date: string; passed: boolean; isToday: boolean }[] = []
  for (let i = 0; i < daysInYear.value; i++) {
    const d = new Date(props.year, 0, 1 + i)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    result.push({
      date: key,
      passed: key < todayStr,
      isToday: key === todayStr,
    })
  }
  return result
})

const passedCount = computed(() => days.value.filter(d => d.passed).length)

function formatDate(date: string): string {
  if (!date) return ''
  const d = new Date(date + 'T00:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>

<template>
  <div class="calendar-wrap">
    <div class="year-dots">
      <div
        v-for="day in days"
        :key="day.date"
        class="dot"
        :class="{
          passed: day.passed,
          today: day.isToday,
        }"
        :title="formatDate(day.date)"
      />
    </div>
    <p class="progress-label">{{ passedCount }} / {{ daysInYear }} days</p>
  </div>
</template>

<style scoped>
.calendar-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.year-dots {
  display: grid;
  grid-template-columns: repeat(20, 14px);
  grid-auto-rows: 14px;
  gap: 2px;
}

.dot {
  width: 12px;
  height: 12px;
  margin: auto;
  border-radius: 9999px;
  background: transparent;
  box-shadow: inset 0 0 0 1.5px var(--app-text);
}

.dot.passed {
  background: var(--app-text);
  box-shadow: none;
}

.dot.today {
  width: 14px;
  height: 14px;
  background: var(--app-text);
  box-shadow: none;
  outline: 2px solid var(--app-text);
  outline-offset: 2px;
  border-radius: 9999px;
}

.progress-label {
  margin: 12px 0 0;
  font-size: 0.75rem;
  color: var(--app-text-muted);
}
</style>
