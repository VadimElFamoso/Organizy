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
  priority?: string | null
  project_id?: string | null
  column_id?: string | null
  due_date?: string | null
  is_done: boolean
  done_at?: string | null
  sort_order: number
  created_at: string
}

// ==========================================================================
// Project Types
// ==========================================================================

export type ProjectMethod = 'kanban' | 'eisenhower' | 'classic'

export interface ProjectColumn {
  id: string
  name: string
  color: string
  sort_order: number
  created_at: string
}

export interface TodoProject {
  id: string
  name: string
  method: ProjectMethod
  sort_order: number
  columns: ProjectColumn[]
  item_count: number
  created_at: string
}

export interface TodoProjectDetail extends Omit<TodoProject, 'item_count'> {
  items: TaskItem[]
  done_items: TaskItem[]
}

export interface TaskItem {
  id: string
  project_id: string
  column_id?: string | null
  title: string
  description?: string | null
  priority?: string | null
  due_date?: string | null
  is_done: boolean
  done_at?: string | null
  sort_order: number
  created_at: string
}

export interface TodayTaskItem {
  task: DailyTask
  completed: boolean
}

// ==========================================================================
// Budget Types
// ==========================================================================

export interface BankAccount {
  id: string
  name: string
  type: 'courant' | 'epargne' | 'prepaye'
  initial_balance: number
  is_default: boolean
  computed_balance: number
  created_at: string
}

export interface BudgetTransaction {
  id: string
  type: 'expense' | 'income'
  amount: number
  category: string
  description?: string | null
  transaction_date: string
  bank_account_id?: string | null
  bank_account_name?: string | null
  created_at: string
}

export interface BudgetSubscription {
  id: string
  name: string
  amount: number
  category: string
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly'
  start_date: string
  description?: string | null
  is_active: boolean
  bank_account_id?: string | null
  bank_account_name?: string | null
  created_at: string
}

export interface CategoryBreakdown {
  category: string
  total: number
}

export interface BudgetMonthlySummary {
  start: string
  end: string
  total_income: number
  total_expenses: number
  balance: number
  account_balance: number
  income_by_category: CategoryBreakdown[]
  expenses_by_category: CategoryBreakdown[]
}

export interface ComparisonBucket {
  label: string
  income: number
  expenses: number
}

export interface BalancePoint {
  date: string
  balance: number
}

export interface UpcomingBilling {
  subscription_id: string
  name: string
  amount: number
  category: string
  frequency: string
  next_date: string
}

export interface BudgetSummaryItem {
  month_balance: number
  total_income: number
  total_expenses: number
  upcoming_count: number
}

export interface DashboardTodoItem {
  id: string
  title: string
  priority: string | null
  due_date: string | null
  project_id: string
  project_name: string
}

export interface DashboardData {
  today_tasks: TodayTaskItem[]
  year_days: DayStats[]
  workout_summary: WorkoutSummary
  top_todos: DashboardTodoItem[]
  budget_summary: BudgetSummaryItem | null
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
  // Todos (legacy — dashboard only)
  // ==========================================================================

  async getTopTodos(limit = 5): Promise<TodoItem[]> {
    return this.fetch<TodoItem[]>(`/todos/top?limit=${limit}`)
  }

  // ==========================================================================
  // Projects
  // ==========================================================================

  async getProjects(): Promise<TodoProject[]> {
    return this.fetch<TodoProject[]>('/projects/')
  }

  async createProject(data: { name: string; method: ProjectMethod }): Promise<TodoProject> {
    return this.fetch<TodoProject>('/projects/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getProject(id: string): Promise<TodoProjectDetail> {
    return this.fetch<TodoProjectDetail>(`/projects/${id}`)
  }

  async updateProject(id: string, data: { name?: string }): Promise<TodoProject> {
    return this.fetch<TodoProject>(`/projects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteProject(id: string): Promise<void> {
    return this.fetch(`/projects/${id}`, { method: 'DELETE' })
  }

  // Project columns
  async createProjectColumn(projectId: string, data: { name: string; color?: string }): Promise<ProjectColumn> {
    return this.fetch<ProjectColumn>(`/projects/${projectId}/columns`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateProjectColumn(projectId: string, columnId: string, data: { name?: string; color?: string }): Promise<ProjectColumn> {
    return this.fetch<ProjectColumn>(`/projects/${projectId}/columns/${columnId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteProjectColumn(projectId: string, columnId: string): Promise<void> {
    return this.fetch(`/projects/${projectId}/columns/${columnId}`, { method: 'DELETE' })
  }

  async reorderProjectColumns(projectId: string, columns: { id: string; sort_order: number }[]): Promise<void> {
    return this.fetch(`/projects/${projectId}/columns/reorder`, {
      method: 'POST',
      body: JSON.stringify({ columns }),
    })
  }

  // Project tasks
  async getProjectTasks(projectId: string): Promise<TaskItem[]> {
    return this.fetch<TaskItem[]>(`/projects/${projectId}/tasks`)
  }

  async getProjectDoneTasks(projectId: string, limit = 50, offset = 0): Promise<TaskItem[]> {
    return this.fetch<TaskItem[]>(`/projects/${projectId}/tasks/done?limit=${limit}&offset=${offset}`)
  }

  async createProjectTask(projectId: string, data: { title: string; description?: string; column_id?: string; priority?: string; due_date?: string; sort_order?: number }): Promise<TaskItem> {
    return this.fetch<TaskItem>(`/projects/${projectId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateProjectTask(projectId: string, taskId: string, data: Partial<{ title: string; description: string | null; column_id: string | null; priority: string | null; due_date: string | null; is_done: boolean; sort_order: number }>): Promise<TaskItem> {
    return this.fetch<TaskItem>(`/projects/${projectId}/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteProjectTask(projectId: string, taskId: string): Promise<void> {
    return this.fetch(`/projects/${projectId}/tasks/${taskId}`, { method: 'DELETE' })
  }

  async bulkDeleteProjectTasks(projectId: string, ids: string[]): Promise<void> {
    return this.fetch(`/projects/${projectId}/tasks/bulk-delete`, {
      method: 'POST',
      body: JSON.stringify({ ids }),
    })
  }

  async reorderProjectTasks(projectId: string, items: { id: string; column_id?: string | null; sort_order: number }[]): Promise<void> {
    return this.fetch(`/projects/${projectId}/tasks/reorder`, {
      method: 'POST',
      body: JSON.stringify({ items }),
    })
  }

  // ==========================================================================
  // Budget — Bank Accounts
  // ==========================================================================

  async getBankAccounts(): Promise<BankAccount[]> {
    return this.fetch<BankAccount[]>('/budget/accounts')
  }

  async createBankAccount(data: { name: string; type: string; initial_balance?: number; is_default?: boolean }): Promise<BankAccount> {
    return this.fetch<BankAccount>('/budget/accounts', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async setupBankAccounts(accounts: { name: string; type: string; initial_balance?: number; is_default?: boolean }[]): Promise<BankAccount[]> {
    return this.fetch<BankAccount[]>('/budget/accounts/setup', {
      method: 'POST',
      body: JSON.stringify({ accounts }),
    })
  }

  async updateBankAccount(id: string, data: Partial<{ name: string; type: string; initial_balance: number; is_default: boolean }>): Promise<BankAccount> {
    return this.fetch<BankAccount>(`/budget/accounts/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteBankAccount(id: string): Promise<void> {
    return this.fetch(`/budget/accounts/${id}`, { method: 'DELETE' })
  }

  // ==========================================================================
  // Budget — Transactions & Subscriptions
  // ==========================================================================

  async getBudgetTransactions(params?: { start?: string; end?: string; type?: string; category?: string; bank_account_id?: string }): Promise<BudgetTransaction[]> {
    const query = new URLSearchParams()
    if (params?.start) query.set('start', params.start)
    if (params?.end) query.set('end', params.end)
    if (params?.type) query.set('type', params.type)
    if (params?.category) query.set('category', params.category)
    if (params?.bank_account_id) query.set('bank_account_id', params.bank_account_id)
    const qs = query.toString()
    return this.fetch<BudgetTransaction[]>(`/budget/transactions${qs ? `?${qs}` : ''}`)
  }

  async createBudgetTransaction(data: { type: string; amount: number; category: string; description?: string; transaction_date: string; bank_account_id?: string | null }): Promise<BudgetTransaction> {
    return this.fetch<BudgetTransaction>('/budget/transactions', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateBudgetTransaction(id: string, data: Partial<{ type: string; amount: number; category: string; description: string | null; transaction_date: string; bank_account_id: string | null }>): Promise<BudgetTransaction> {
    return this.fetch<BudgetTransaction>(`/budget/transactions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteBudgetTransaction(id: string): Promise<void> {
    return this.fetch(`/budget/transactions/${id}`, { method: 'DELETE' })
  }

  async getBudgetSubscriptions(params?: { bank_account_id?: string }): Promise<BudgetSubscription[]> {
    const query = new URLSearchParams()
    if (params?.bank_account_id) query.set('bank_account_id', params.bank_account_id)
    const qs = query.toString()
    return this.fetch<BudgetSubscription[]>(`/budget/subscriptions${qs ? `?${qs}` : ''}`)
  }

  async createBudgetSubscription(data: { name: string; amount: number; category: string; frequency: string; start_date: string; description?: string; bank_account_id?: string | null }): Promise<BudgetSubscription> {
    return this.fetch<BudgetSubscription>('/budget/subscriptions', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateBudgetSubscription(id: string, data: Partial<{ name: string; amount: number; category: string; frequency: string; start_date: string; description: string | null; is_active: boolean; bank_account_id: string | null }>): Promise<BudgetSubscription> {
    return this.fetch<BudgetSubscription>(`/budget/subscriptions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteBudgetSubscription(id: string): Promise<void> {
    return this.fetch(`/budget/subscriptions/${id}`, { method: 'DELETE' })
  }

  // ==========================================================================
  // Budget — Summary & Analytics
  // ==========================================================================

  async getBudgetSummary(start: string, end: string, bankAccountId?: string): Promise<BudgetMonthlySummary> {
    const query = new URLSearchParams({ start, end })
    if (bankAccountId) query.set('bank_account_id', bankAccountId)
    return this.fetch<BudgetMonthlySummary>(`/budget/summary?${query}`)
  }

  async getBudgetComparison(start: string, end: string, groupBy: string, bankAccountId?: string): Promise<ComparisonBucket[]> {
    const query = new URLSearchParams({ start, end, group_by: groupBy })
    if (bankAccountId) query.set('bank_account_id', bankAccountId)
    return this.fetch<ComparisonBucket[]>(`/budget/summary/comparison?${query}`)
  }

  async getBudgetBalanceHistory(start: string, end: string, bankAccountId?: string): Promise<BalancePoint[]> {
    const query = new URLSearchParams({ start, end })
    if (bankAccountId) query.set('bank_account_id', bankAccountId)
    return this.fetch<BalancePoint[]>(`/budget/summary/balance-history?${query}`)
  }

  async getBudgetCategories(type: 'income' | 'expense', start: string, end: string, bankAccountId?: string): Promise<CategoryBreakdown[]> {
    const query = new URLSearchParams({ type, start, end })
    if (bankAccountId) query.set('bank_account_id', bankAccountId)
    return this.fetch<CategoryBreakdown[]>(`/budget/summary/categories?${query}`)
  }

  async getBudgetUpcoming(bankAccountId?: string): Promise<UpcomingBilling[]> {
    const query = new URLSearchParams()
    if (bankAccountId) query.set('bank_account_id', bankAccountId)
    const qs = query.toString()
    return this.fetch<UpcomingBilling[]>(`/budget/subscriptions/upcoming${qs ? `?${qs}` : ''}`)
  }

  // ==========================================================================
  // Dashboard
  // ==========================================================================

  async getDashboard(): Promise<DashboardData> {
    return this.fetch<DashboardData>('/dashboard/')
  }
}

export const api = new ApiClient()
