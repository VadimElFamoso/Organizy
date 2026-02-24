import { ref, computed } from 'vue'
import { api, type TodoProjectDetail, type TaskItem, type ProjectColumn } from '@/services/api'

export function useProjectBoard(projectId: string) {
  const project = ref<TodoProjectDetail | null>(null)
  const isLoading = ref(false)

  const columns = computed(() => project.value?.columns ?? [])
  const items = computed(() => project.value?.items ?? [])
  const doneItems = computed(() => project.value?.done_items ?? [])

  const itemsByColumn = computed(() => {
    const map: Record<string, TaskItem[]> = {}
    for (const col of columns.value) {
      map[col.id] = []
    }
    for (const item of items.value) {
      if (item.column_id && map[item.column_id]) {
        map[item.column_id].push(item)
      }
    }
    // Sort items within each column
    for (const key of Object.keys(map)) {
      map[key].sort((a, b) => a.sort_order - b.sort_order)
    }
    return map
  })

  async function fetchProject() {
    isLoading.value = true
    try {
      project.value = await api.getProject(projectId)
    } finally {
      isLoading.value = false
    }
  }

  async function updateProjectName(name: string) {
    await api.updateProject(projectId, { name })
    if (project.value) project.value.name = name
  }

  // Column operations
  async function addColumn(name: string, color?: string) {
    const col = await api.createProjectColumn(projectId, { name, color })
    if (project.value) project.value.columns.push(col)
    return col
  }

  async function updateColumn(columnId: string, data: { name?: string; color?: string }) {
    const updated = await api.updateProjectColumn(projectId, columnId, data)
    if (project.value) {
      const idx = project.value.columns.findIndex(c => c.id === columnId)
      if (idx !== -1) project.value.columns[idx] = updated
    }
  }

  async function deleteColumn(columnId: string) {
    await api.deleteProjectColumn(projectId, columnId)
    if (project.value) {
      project.value.columns = project.value.columns.filter(c => c.id !== columnId)
    }
  }

  async function reorderColumns(cols: { id: string; sort_order: number }[]) {
    await api.reorderProjectColumns(projectId, cols)
    if (project.value) {
      for (const c of cols) {
        const col = project.value.columns.find(x => x.id === c.id)
        if (col) col.sort_order = c.sort_order
      }
      project.value.columns.sort((a, b) => a.sort_order - b.sort_order)
    }
  }

  // Task operations
  async function createTask(data: { title: string; description?: string; column_id?: string; priority?: string; due_date?: string }) {
    const task = await api.createProjectTask(projectId, data)
    if (project.value) project.value.items.push(task)
    return task
  }

  async function updateTask(taskId: string, data: Partial<{ title: string; description: string | null; column_id: string | null; priority: string | null; due_date: string | null; is_done: boolean; sort_order: number }>) {
    const updated = await api.updateProjectTask(projectId, taskId, data)
    if (!project.value) return updated

    if (updated.is_done) {
      project.value.items = project.value.items.filter(t => t.id !== taskId)
      project.value.done_items.unshift(updated)
    } else {
      const idx = project.value.items.findIndex(t => t.id === taskId)
      if (idx !== -1) {
        project.value.items[idx] = updated
      } else {
        // Was in done list, move back
        project.value.done_items = project.value.done_items.filter(t => t.id !== taskId)
        project.value.items.push(updated)
      }
    }
    return updated
  }

  async function deleteTask(taskId: string) {
    await api.deleteProjectTask(projectId, taskId)
    if (project.value) {
      project.value.items = project.value.items.filter(t => t.id !== taskId)
      project.value.done_items = project.value.done_items.filter(t => t.id !== taskId)
    }
  }

  async function bulkDeleteTasks(ids: string[]) {
    await api.bulkDeleteProjectTasks(projectId, ids)
    if (project.value) {
      project.value.items = project.value.items.filter(t => !ids.includes(t.id))
      project.value.done_items = project.value.done_items.filter(t => !ids.includes(t.id))
    }
  }

  async function reorderTasks(reorderItems: { id: string; column_id?: string | null; sort_order: number }[]) {
    await api.reorderProjectTasks(projectId, reorderItems)
    if (project.value) {
      for (const item of reorderItems) {
        const task = project.value.items.find(t => t.id === item.id)
        if (task) {
          task.sort_order = item.sort_order
          if (item.column_id !== undefined) task.column_id = item.column_id
        }
      }
    }
  }

  return {
    project,
    columns,
    items,
    doneItems,
    itemsByColumn,
    isLoading,
    fetchProject,
    updateProjectName,
    addColumn,
    updateColumn,
    deleteColumn,
    reorderColumns,
    createTask,
    updateTask,
    deleteTask,
    bulkDeleteTasks,
    reorderTasks,
  }
}
