const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export class HttpError extends Error {
  public readonly statusCode: number
  public readonly response?: { status: number; data: unknown }
  public readonly retryable: boolean

  constructor(
    message: string,
    statusCode: number,
    response?: { status: number; data: unknown },
    retryable = false
  ) {
    super(message)
    this.name = 'HttpError'
    this.statusCode = statusCode
    this.response = response
    this.retryable = retryable
  }
}

function dispatchSessionExpired() {
  window.dispatchEvent(new CustomEvent('auth:session-expired'))
}

export type SubscriptionStatus = 'trialing' | 'active' | 'past_due' | 'canceled' | 'expired'
export type SubscriptionPlan = 'free' | 'starter' | 'pro' | 'unlimited' | 'team'

export interface User {
  id: string
  email: string
  name: string
  picture?: string
  preferences: UserPreferences
  subscription_status: SubscriptionStatus
  subscription_plan: SubscriptionPlan
  subscription_end_date?: string
  trial_started_at?: string
  created_at: string
}

export interface PlanInfo {
  name: string
  tier: string
  price_id: string
  price_id_yearly: string
  price_monthly: number
  price_yearly: number
  features: string[]
  limits: Record<string, number>
  available: boolean
  trial_days: number
  is_popular: boolean
}

export interface SubscriptionInfo {
  status: string
  plan: string
  end_date?: string
  trial_days_remaining?: number
  has_active_access: boolean
}

export interface UserPreferences {
  // Add your app-specific preferences here
}

export interface UserAnalytics {
  // Add your app-specific analytics fields here
}

// ==========================================================================
// Organizy Types
// ==========================================================================

export interface DailyTask {
  id: string
  name: string
  description?: string | null
  is_active: boolean
  sort_order: number
  created_at: string
}

export interface Completion {
  id: string
  task_id: string
  completed_date: string
}

export interface DayStats {
  date: string
  completed: number
  total: number
  ratio: number
}

export interface YearStats {
  year: number
  days: DayStats[]
}

export interface RangeStats {
  start: string
  end: string
  days: DayStats[]
}

export interface ExerciseItem {
  id?: string
  name: string
  notes?: string | null
  sort_order: number
}

export interface WorkoutItem {
  id: string
  workout_type: string
  notes?: string | null
  workout_date: string
  duration_minutes?: number | null
  exercises: ExerciseItem[]
  created_at: string
}

export interface WorkoutSummary {
  total_workouts: number
  current_streak: number
  last_workout: WorkoutItem | null
  today_workouts: WorkoutItem[]
}

export interface WorkoutCalendarDay {
  date: string
  count: number
}

export interface WorkoutPreset {
  id: string
  name: string
  workout_type: string
  duration_minutes?: number | null
  exercises: ExerciseItem[]
  created_at: string
}

export interface TodoItem {
  id: string
  title: string
  description?: string | null
  priority: string
  is_done: boolean
  done_at?: string | null
  sort_order: number
  created_at: string
}

export interface TodayTaskItem {
  task: DailyTask
  completed: boolean
}

export interface DashboardData {
  today_tasks: TodayTaskItem[]
  year_days: DayStats[]
  workout_summary: WorkoutSummary
  top_todos: TodoItem[]
}

interface SessionResponse {
  authenticated: boolean
  user: User | null
}

class ApiClient {
  private _isAuthenticated: boolean = false

  /**
   * Check if the user has an active session via httpOnly cookies.
   */
  async checkSession(): Promise<SessionResponse> {
    try {
      const response = await fetch(`${API_BASE}/auth/session`, {
        method: 'GET',
        credentials: 'include',
      })

      if (!response.ok) {
        this._isAuthenticated = false
        return { authenticated: false, user: null }
      }

      const data: SessionResponse = await response.json()
      this._isAuthenticated = data.authenticated
      return data
    } catch {
      this._isAuthenticated = false
      return { authenticated: false, user: null }
    }
  }

  isAuthenticated(): boolean {
    return this._isAuthenticated
  }

  private async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    let response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include',
    })

    // If unauthorized, try to refresh token
    if (response.status === 401) {
      const refreshed = await this.tryRefreshToken()
      if (refreshed) {
        response = await fetch(`${API_BASE}${endpoint}`, {
          ...options,
          headers,
          credentials: 'include',
        })
      }
    }

    if (!response.ok) {
      if (response.status === 401) {
        this._isAuthenticated = false
        throw new HttpError('Not authenticated', 401)
      }
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }))
      const message = errorData.detail?.message || errorData.detail || 'Request failed'
      throw new HttpError(message, response.status, {
        status: response.status,
        data: errorData,
      })
    }

    if (response.status === 204) {
      return undefined as T
    }

    return response.json()
  }

  private async tryRefreshToken(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!response.ok) {
        this._isAuthenticated = false
        dispatchSessionExpired()
        return false
      }

      this._isAuthenticated = true
      return true
    } catch {
      this._isAuthenticated = false
      dispatchSessionExpired()
      return false
    }
  }

  // ==========================================================================
  // Auth
  // ==========================================================================

  getGoogleLoginUrl(): string {
    return `${API_BASE}/auth/google/login`
  }

  async getCurrentUser(): Promise<User> {
    return this.fetch<User>('/auth/me')
  }

  async logout(): Promise<void> {
    await this.fetch('/auth/logout', { method: 'POST' })
    this._isAuthenticated = false
  }

  // ==========================================================================
  // User
  // ==========================================================================

  async getUserPreferences(): Promise<UserPreferences> {
    return this.fetch<UserPreferences>('/users/me/preferences')
  }

  async updateUserPreferences(prefs: Partial<UserPreferences>): Promise<UserPreferences> {
    return this.fetch<UserPreferences>('/users/me/preferences', {
      method: 'PATCH',
      body: JSON.stringify(prefs),
    })
  }

  // ==========================================================================
  // Payments
  // ==========================================================================

  async getPlans(): Promise<PlanInfo[]> {
    return this.fetch<PlanInfo[]>('/payments/plans')
  }

  async createCheckoutSession(priceId: string): Promise<{ checkout_url: string }> {
    return this.fetch('/payments/create-checkout-session', {
      method: 'POST',
      body: JSON.stringify({ price_id: priceId }),
    })
  }

  async createPortalSession(): Promise<{ portal_url: string }> {
    return this.fetch('/payments/create-portal-session', {
      method: 'POST',
    })
  }

  async getSubscription(): Promise<SubscriptionInfo> {
    return this.fetch('/payments/subscription')
  }

  async checkTrialEligible(): Promise<{ eligible: boolean }> {
    return this.fetch('/payments/trial-eligible')
  }

  async changePlan(newPriceId: string): Promise<{ success: boolean; new_plan: string }> {
    return this.fetch('/payments/change-plan', {
      method: 'POST',
      body: JSON.stringify({ new_price_id: newPriceId }),
    })
  }

  // ==========================================================================
  // Analytics
  // ==========================================================================

  async getUserAnalytics(): Promise<UserAnalytics> {
    return this.fetch<UserAnalytics>('/analytics/me')
  }

  // ==========================================================================
  // Daily Tasks
  // ==========================================================================

  async getDailyTasks(): Promise<DailyTask[]> {
    return this.fetch<DailyTask[]>('/daily-tasks/')
  }

  async createDailyTask(data: { name: string; description?: string; sort_order?: number }): Promise<DailyTask> {
    return this.fetch<DailyTask>('/daily-tasks/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateDailyTask(id: string, data: Partial<{ name: string; description: string | null; is_active: boolean; sort_order: number }>): Promise<DailyTask> {
    return this.fetch<DailyTask>(`/daily-tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteDailyTask(id: string): Promise<void> {
    return this.fetch(`/daily-tasks/${id}`, { method: 'DELETE' })
  }

  async toggleCompletion(taskId: string, date: string): Promise<Completion | null> {
    return this.fetch<Completion | null>('/daily-tasks/completions/toggle', {
      method: 'POST',
      body: JSON.stringify({ task_id: taskId, date }),
    })
  }

  async getCompletions(start: string, end: string): Promise<Completion[]> {
    return this.fetch<Completion[]>(`/daily-tasks/completions?start=${start}&end=${end}`)
  }

  async getYearStats(year: number): Promise<YearStats> {
    return this.fetch<YearStats>(`/daily-tasks/stats/year?year=${year}`)
  }

  async getRangeStats(start: string, end: string): Promise<RangeStats> {
    return this.fetch<RangeStats>(`/daily-tasks/stats/range?start=${start}&end=${end}`)
  }

  // ==========================================================================
  // Workouts
  // ==========================================================================

  async getWorkouts(limit = 50, offset = 0): Promise<WorkoutItem[]> {
    return this.fetch<WorkoutItem[]>(`/workouts/?limit=${limit}&offset=${offset}`)
  }

  async createWorkout(data: { workout_type: string; notes?: string; workout_date?: string; duration_minutes?: number; exercises?: ExerciseItem[] }): Promise<WorkoutItem> {
    return this.fetch<WorkoutItem>('/workouts/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateWorkout(id: string, data: Partial<{ workout_type: string; notes: string | null; duration_minutes: number | null; exercises: ExerciseItem[] }>): Promise<WorkoutItem> {
    return this.fetch<WorkoutItem>(`/workouts/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async getWorkoutsByDate(workoutDate: string): Promise<WorkoutItem[]> {
    return this.fetch<WorkoutItem[]>(`/workouts/by-date?workout_date=${workoutDate}`)
  }

  async deleteWorkout(id: string): Promise<void> {
    return this.fetch(`/workouts/${id}`, { method: 'DELETE' })
  }

  async getWorkoutSummary(): Promise<WorkoutSummary> {
    return this.fetch<WorkoutSummary>('/workouts/summary')
  }

  async getWorkoutCalendar(year: number, month: number): Promise<WorkoutCalendarDay[]> {
    return this.fetch<WorkoutCalendarDay[]>(`/workouts/calendar?year=${year}&month=${month}`)
  }

  async getWorkoutTypes(): Promise<string[]> {
    return this.fetch<string[]>('/workouts/types')
  }

  async getWorkoutPresets(): Promise<WorkoutPreset[]> {
    return this.fetch<WorkoutPreset[]>('/workouts/presets')
  }

  async createWorkoutPreset(data: { name: string; workout_type: string; duration_minutes?: number | null; exercises?: { name: string; notes?: string | null; sort_order: number }[] }): Promise<WorkoutPreset> {
    return this.fetch<WorkoutPreset>('/workouts/presets', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateWorkoutPreset(id: string, data: Partial<{ name: string; workout_type: string; duration_minutes: number | null; exercises: { name: string; notes?: string | null; sort_order: number }[] }>): Promise<WorkoutPreset> {
    return this.fetch<WorkoutPreset>(`/workouts/presets/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteWorkoutPreset(id: string): Promise<void> {
    return this.fetch(`/workouts/presets/${id}`, { method: 'DELETE' })
  }

  // ==========================================================================
  // Todos
  // ==========================================================================

  async getTodos(): Promise<TodoItem[]> {
    return this.fetch<TodoItem[]>('/todos/')
  }

  async getDoneTodos(limit = 50, offset = 0): Promise<TodoItem[]> {
    return this.fetch<TodoItem[]>(`/todos/done?limit=${limit}&offset=${offset}`)
  }

  async createTodo(data: { title: string; description?: string; priority?: string; sort_order?: number }): Promise<TodoItem> {
    return this.fetch<TodoItem>('/todos/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateTodo(id: string, data: Partial<{ title: string; description: string | null; priority: string; is_done: boolean; sort_order: number }>): Promise<TodoItem> {
    return this.fetch<TodoItem>(`/todos/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteTodo(id: string): Promise<void> {
    return this.fetch(`/todos/${id}`, { method: 'DELETE' })
  }

  async bulkDeleteTodos(ids: string[]): Promise<void> {
    return this.fetch('/todos/bulk-delete', {
      method: 'POST',
      body: JSON.stringify({ ids }),
    })
  }

  async reorderTodos(items: { id: string; priority: string; sort_order: number }[]): Promise<void> {
    return this.fetch('/todos/reorder', {
      method: 'POST',
      body: JSON.stringify({ items }),
    })
  }

  async getTopTodos(limit = 5): Promise<TodoItem[]> {
    return this.fetch<TodoItem[]>(`/todos/top?limit=${limit}`)
  }

  // ==========================================================================
  // Dashboard
  // ==========================================================================

  async getDashboard(): Promise<DashboardData> {
    return this.fetch<DashboardData>('/dashboard/')
  }
}

export const api = new ApiClient()
