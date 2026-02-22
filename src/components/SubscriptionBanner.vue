<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/composables/useAuth'
import { useSubscription } from '@/composables/useSubscription'
import { Crown, Clock, Sparkles, LogIn, XCircle, AlertTriangle } from 'lucide-vue-next'

const { user, isAuthenticated, loginWithGoogle } = useAuth()
const { isTrialing, isActive, isCanceled, isPastDue, trialDaysRemaining } = useSubscription(user)

const daysRemaining = computed(() => {
  if (!user.value?.subscription_end_date) return 0
  const endDate = new Date(user.value.subscription_end_date)
  const now = new Date()
  const remaining = Math.ceil((endDate.getTime() - now.getTime()) / (24 * 60 * 60 * 1000))
  return Math.max(0, remaining)
})

const bannerType = computed(() => {
  if (!isAuthenticated.value) return 'login'
  if (isActive.value) return 'none'
  if (isTrialing.value) return 'trial'
  if (isPastDue.value) return 'past_due'
  if (isCanceled.value && daysRemaining.value > 0) return 'canceled'
  return 'subscribe'
})
</script>

<template>
  <!-- No banner for active subscribers -->
  <template v-if="bannerType === 'none'" />

  <!-- Login banner for unauthenticated users -->
  <div v-else-if="bannerType === 'login'" class="banner banner-login">
    <div class="banner-content">
      <LogIn :size="18" />
      <span>
        <strong>Sign in</strong> to access all features
      </span>
    </div>
    <Button size="sm" variant="outline" class="banner-btn" @click="loginWithGoogle()">
      Sign in with Google
    </Button>
  </div>

  <!-- Trial info banner -->
  <div v-else-if="bannerType === 'trial'" class="banner banner-trial">
    <div class="banner-content">
      <Clock :size="18" />
      <span>
        <strong>{{ trialDaysRemaining }} days</strong> left in your free trial
      </span>
    </div>
    <RouterLink to="/settings" class="banner-link">
      Manage subscription
    </RouterLink>
  </div>

  <!-- Canceled banner -->
  <div v-else-if="bannerType === 'canceled'" class="banner banner-canceled">
    <div class="banner-content">
      <XCircle :size="18" />
      <span>
        Your subscription is canceled. Access ends in <strong>{{ daysRemaining }} days</strong>.
      </span>
    </div>
    <RouterLink to="/pricing" class="banner-link">
      Resubscribe
    </RouterLink>
  </div>

  <!-- Past due banner -->
  <div v-else-if="bannerType === 'past_due'" class="banner banner-past-due">
    <div class="banner-content">
      <AlertTriangle :size="18" />
      <span>
        <strong>Payment failed.</strong> Update your payment method to continue.
      </span>
    </div>
    <RouterLink to="/pricing" class="banner-link-urgent">
      Update Payment
    </RouterLink>
  </div>

  <!-- Subscribe banner -->
  <div v-else-if="bannerType === 'subscribe'" class="banner banner-subscribe">
    <div class="banner-content">
      <Crown :size="18" />
      <span>
        <strong>Start your 7-day free trial</strong> to unlock all features
      </span>
    </div>
    <RouterLink to="/pricing">
      <Button size="sm" class="banner-btn-cta">
        <Sparkles :size="14" />
        Start Free Trial
      </Button>
    </RouterLink>
  </div>
</template>

<style scoped>
.banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 10px 24px;
  font-size: 0.875rem;
  flex-wrap: wrap;
  background: var(--app-surface-3);
  border-bottom: 1px solid var(--app-border-hover);
  color: var(--app-text);
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.banner-content svg {
  color: var(--app-text-muted);
  flex-shrink: 0;
}

.banner-login .banner-content svg {
  color: var(--theme-accent);
}

.banner-trial .banner-content svg {
  color: var(--app-text-muted);
}

.banner-canceled .banner-content svg {
  color: #fb923c;
}

.banner-past-due .banner-content svg {
  color: #ef4444;
}

.banner-subscribe .banner-content svg {
  color: var(--theme-accent);
}

.banner-btn {
  background: transparent;
  border: 1px solid var(--app-border-hover);
  color: var(--app-text);
  font-size: 0.8rem;
  padding: 6px 12px;
  height: auto;
}

.banner-btn:hover {
  background: var(--app-surface-2);
  border-color: var(--theme-accent);
}

.banner-btn-cta {
  background: var(--theme-accent);
  border: none;
  color: white;
  font-size: 0.8rem;
  padding: 6px 14px;
  height: auto;
  display: flex;
  align-items: center;
  gap: 6px;
}

.banner-btn-cta:hover {
  background: var(--theme-accent-hover);
}

.banner-link {
  color: var(--app-text-muted);
  font-size: 0.8rem;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.banner-link:hover {
  color: var(--app-text);
}

.banner-link-urgent {
  color: #f87171;
  font-size: 0.8rem;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.banner-link-urgent:hover {
  color: #fca5a5;
}

@media (max-width: 640px) {
  .banner {
    flex-direction: column;
    gap: 10px;
    text-align: center;
    padding: 12px 16px;
  }
}
</style>
