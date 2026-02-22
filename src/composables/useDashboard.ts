import { ref } from 'vue'
import { api, type DashboardData } from '@/services/api'

const dashboard = ref<DashboardData | null>(null)
const isLoading = ref(false)

export function useDashboard() {
  async function fetchDashboard() {
    if (!dashboard.value) isLoading.value = true
    try {
      dashboard.value = await api.getDashboard()
    } finally {
      isLoading.value = false
    }
  }

  return {
    dashboard,
    isLoading,
    fetchDashboard,
  }
}
