import { ref, computed } from 'vue'
import { api, type TodoItem } from '@/services/api'

const todos = ref<TodoItem[]>([])
const doneTodos = ref<TodoItem[]>([])
const isLoading = ref(false)

export function useTodos() {
  const urgentTodos = computed(() => todos.value.filter(t => t.priority === 'urgent'))
  const highTodos = computed(() => todos.value.filter(t => t.priority === 'high'))
  const mediumTodos = computed(() => todos.value.filter(t => t.priority === 'medium'))
  const lowTodos = computed(() => todos.value.filter(t => t.priority === 'low'))

  async function fetchTodos() {
    isLoading.value = true
    try {
      todos.value = await api.getTodos()
    } finally {
      isLoading.value = false
    }
  }

  async function fetchDoneTodos(limit = 50, offset = 0) {
    doneTodos.value = await api.getDoneTodos(limit, offset)
  }

  async function createTodo(data: { title: string; description?: string; priority?: string }) {
    const todo = await api.createTodo(data)
    todos.value.push(todo)
    return todo
  }

  async function updateTodo(id: string, data: Partial<{ title: string; description: string | null; priority: string; is_done: boolean; sort_order: number }>) {
    const updated = await api.updateTodo(id, data)
    if (updated.is_done) {
      todos.value = todos.value.filter(t => t.id !== id)
      doneTodos.value.unshift(updated)
    } else {
      const idx = todos.value.findIndex(t => t.id === id)
      if (idx !== -1) {
        todos.value[idx] = updated
      } else {
        // Was in done list, move back to active
        doneTodos.value = doneTodos.value.filter(t => t.id !== id)
        todos.value.push(updated)
      }
    }
    return updated
  }

  async function deleteTodo(id: string) {
    await api.deleteTodo(id)
    todos.value = todos.value.filter(t => t.id !== id)
    doneTodos.value = doneTodos.value.filter(t => t.id !== id)
  }

  async function bulkDelete(ids: string[]) {
    await api.bulkDeleteTodos(ids)
    doneTodos.value = doneTodos.value.filter(t => !ids.includes(t.id))
    todos.value = todos.value.filter(t => !ids.includes(t.id))
  }

  async function reorder(items: { id: string; priority: string; sort_order: number }[]) {
    await api.reorderTodos(items)
    // Update local state
    for (const item of items) {
      const todo = todos.value.find(t => t.id === item.id)
      if (todo) {
        todo.priority = item.priority
        todo.sort_order = item.sort_order
      }
    }
  }

  return {
    todos,
    doneTodos,
    urgentTodos,
    highTodos,
    mediumTodos,
    lowTodos,
    isLoading,
    fetchTodos,
    fetchDoneTodos,
    createTodo,
    updateTodo,
    deleteTodo,
    bulkDelete,
    reorder,
  }
}
