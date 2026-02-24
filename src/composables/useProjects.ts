import { ref } from 'vue'
import { api, type TodoProject, type ProjectMethod } from '@/services/api'

const projects = ref<TodoProject[]>([])
const isLoading = ref(false)

export function useProjects() {
  async function fetchProjects() {
    isLoading.value = true
    try {
      projects.value = await api.getProjects()
    } finally {
      isLoading.value = false
    }
  }

  async function createProject(name: string, method: ProjectMethod) {
    const project = await api.createProject({ name, method })
    projects.value.push(project)
    return project
  }

  async function deleteProject(id: string) {
    await api.deleteProject(id)
    projects.value = projects.value.filter(p => p.id !== id)
  }

  return {
    projects,
    isLoading,
    fetchProjects,
    createProject,
    deleteProject,
  }
}
