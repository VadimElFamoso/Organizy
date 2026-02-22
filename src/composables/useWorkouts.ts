import { ref } from 'vue'
import { api, type WorkoutItem, type WorkoutSummary, type WorkoutCalendarDay } from '@/services/api'

const workouts = ref<WorkoutItem[]>([])
const summary = ref<WorkoutSummary | null>(null)
const calendarDays = ref<WorkoutCalendarDay[]>([])
const workoutTypes = ref<string[]>([])
const isLoading = ref(false)

export function useWorkouts() {
  async function fetchWorkouts(limit = 50, offset = 0) {
    isLoading.value = true
    try {
      workouts.value = await api.getWorkouts(limit, offset)
    } finally {
      isLoading.value = false
    }
  }

  async function createWorkout(data: { workout_type: string; notes?: string; workout_date: string; duration_minutes?: number }) {
    const workout = await api.createWorkout(data)
    workouts.value.unshift(workout)
    // Refresh summary after creating
    summary.value = await api.getWorkoutSummary()
    return workout
  }

  async function updateWorkout(id: string, data: Partial<{ workout_type: string; notes: string | null; workout_date: string; duration_minutes: number | null }>) {
    const updated = await api.updateWorkout(id, data)
    const idx = workouts.value.findIndex(w => w.id === id)
    if (idx !== -1) workouts.value[idx] = updated
    return updated
  }

  async function deleteWorkout(id: string) {
    await api.deleteWorkout(id)
    workouts.value = workouts.value.filter(w => w.id !== id)
    summary.value = await api.getWorkoutSummary()
  }

  async function fetchSummary() {
    summary.value = await api.getWorkoutSummary()
  }

  async function fetchCalendar(year: number, month: number) {
    calendarDays.value = await api.getWorkoutCalendar(year, month)
  }

  async function fetchWorkoutTypes() {
    workoutTypes.value = await api.getWorkoutTypes()
  }

  return {
    workouts,
    summary,
    calendarDays,
    workoutTypes,
    isLoading,
    fetchWorkouts,
    createWorkout,
    updateWorkout,
    deleteWorkout,
    fetchSummary,
    fetchCalendar,
    fetchWorkoutTypes,
  }
}
