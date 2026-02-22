import { ref } from 'vue'
import { api, type DailyTask, type Completion, type YearStats, type RangeStats } from '@/services/api'

const tasks = ref<DailyTask[]>([])
const completions = ref<Completion[]>([])
const isLoading = ref(false)

export function useDailyTasks() {
  async function fetchTasks() {
    isLoading.value = true
    try {
      tasks.value = await api.getDailyTasks()
    } finally {
      isLoading.value = false
    }
  }

  async function createTask(name: string, description?: string) {
    const task = await api.createDailyTask({ name, description })
    tasks.value.push(task)
    return task
  }

  async function updateTask(id: string, data: Partial<{ name: string; description: string | null; is_active: boolean; sort_order: number }>) {
    const updated = await api.updateDailyTask(id, data)
    const idx = tasks.value.findIndex(t => t.id === id)
    if (idx !== -1) tasks.value[idx] = updated
    return updated
  }

  async function deleteTask(id: string) {
    await api.deleteDailyTask(id)
    tasks.value = tasks.value.filter(t => t.id !== id)
  }

  async function toggleCompletion(taskId: string, date: string) {
    const result = await api.toggleCompletion(taskId, date)
    if (result) {
      completions.value.push(result)
    } else {
      completions.value = completions.value.filter(
        c => !(c.task_id === taskId && c.completed_date === date)
      )
    }
    return result
  }

  async function fetchCompletions(start: string, end: string) {
    completions.value = await api.getCompletions(start, end)
  }

  async function getYearStats(year: number): Promise<YearStats> {
    return api.getYearStats(year)
  }

  async function getRangeStats(start: string, end: string): Promise<RangeStats> {
    return api.getRangeStats(start, end)
  }

  function isCompleted(taskId: string, date: string): boolean {
    return completions.value.some(c => c.task_id === taskId && c.completed_date === date)
  }

  return {
    tasks,
    completions,
    isLoading,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleCompletion,
    fetchCompletions,
    getYearStats,
    getRangeStats,
    isCompleted,
  }
}
