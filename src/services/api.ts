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
}

export const api = new ApiClient()
