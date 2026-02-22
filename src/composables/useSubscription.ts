import { computed, type Ref, type ComputedRef } from 'vue'
import type { User } from '@/services/api'

export interface SubscriptionState {
  isTrialing: ComputedRef<boolean>
  isActive: ComputedRef<boolean>
  isCanceled: ComputedRef<boolean>
  isPastDue: ComputedRef<boolean>
  hasAccess: ComputedRef<boolean>
  needsSubscription: ComputedRef<boolean>
  trialDaysRemaining: ComputedRef<number>
  statusLabel: ComputedRef<string>
  statusColor: ComputedRef<'success' | 'trial' | 'canceled' | 'past_due' | 'expired'>
}

/**
 * Composable for subscription status derived from user data.
 * Use with a reactive user ref from useAuth.
 */
export function useSubscription(user: Ref<User | null>): SubscriptionState {
  const isTrialing = computed(() => user.value?.subscription_status === 'trialing')
  const isActive = computed(() => user.value?.subscription_status === 'active')
  const isPastDue = computed(() => user.value?.subscription_status === 'past_due')

  const trialDaysRemaining = computed(() => {
    if (!user.value?.subscription_end_date) return 0
    const endDate = new Date(user.value.subscription_end_date)
    const now = new Date()
    const remaining = Math.ceil((endDate.getTime() - now.getTime()) / (24 * 60 * 60 * 1000))
    return Math.max(0, remaining)
  })

  const isCanceled = computed(() => {
    if (user.value?.subscription_status !== 'canceled') return false
    if (!user.value?.subscription_end_date) return false
    return new Date(user.value.subscription_end_date) > new Date()
  })

  const hasAccess = computed(() => isActive.value || isTrialing.value || isCanceled.value)
  const needsSubscription = computed(() => !hasAccess.value)

  const statusLabel = computed(() => {
    if (isActive.value) return 'Pro'
    if (isTrialing.value) return 'Trial'
    if (isPastDue.value) return 'Payment Failed'
    if (isCanceled.value) return 'Canceled'
    return 'No Subscription'
  })

  const statusColor = computed((): 'success' | 'trial' | 'canceled' | 'past_due' | 'expired' => {
    if (isActive.value) return 'success'
    if (isTrialing.value) return 'trial'
    if (isPastDue.value) return 'past_due'
    if (isCanceled.value) return 'canceled'
    return 'expired'
  })

  return {
    isTrialing,
    isActive,
    isCanceled,
    isPastDue,
    hasAccess,
    needsSubscription,
    trialDaysRemaining,
    statusLabel,
    statusColor,
  }
}

/**
 * Utility for components that receive user as a prop (non-reactive).
 * Derives subscription state from a user object directly.
 */
export function getSubscriptionStatus(user: User | null | undefined) {
  const status = user?.subscription_status
  const endDate = user?.subscription_end_date

  const isTrialing = status === 'trialing'
  const isActive = status === 'active'
  const isPastDue = status === 'past_due'

  const trialDaysRemaining = (() => {
    if (!endDate) return 0
    const end = new Date(endDate)
    const now = new Date()
    const remaining = Math.ceil((end.getTime() - now.getTime()) / (24 * 60 * 60 * 1000))
    return Math.max(0, remaining)
  })()

  const isCanceled = status === 'canceled' && !!endDate && new Date(endDate) > new Date()
  const hasAccess = isActive || isTrialing || isCanceled
  const needsSubscription = !hasAccess

  const statusLabel = isActive ? 'Pro' : isTrialing ? 'Trial' : isPastDue ? 'Payment Failed' : isCanceled ? 'Canceled' : 'No Subscription'
  const statusColor = isActive ? 'success' : isTrialing ? 'trial' : isPastDue ? 'past_due' : isCanceled ? 'canceled' : 'expired'

  return {
    isTrialing,
    isActive,
    isCanceled,
    isPastDue,
    hasAccess,
    needsSubscription,
    trialDaysRemaining,
    statusLabel,
    statusColor,
  }
}
