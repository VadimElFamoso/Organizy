<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useAuth } from '@/composables/useAuth'
import { api, type PlanInfo, type SubscriptionInfo } from '@/services/api'
import { CalendarCheck, Check, ArrowLeft, Loader2, Clock, CreditCard, AlertTriangle } from 'lucide-vue-next'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const route = useRoute()
const { user, isAuthenticated } = useAuth()
const { showToast } = useToast()

const plans = ref<PlanInfo[]>([])
const subscription = ref<SubscriptionInfo | null>(null)
const isLoading = ref(true)
const processingPlan = ref<string | null>(null)
const billingCycle = ref<'monthly' | 'yearly'>('monthly')

const trialDaysRemaining = computed(() => {
  if (!user.value?.subscription_end_date) return 0
  const trialEnd = new Date(user.value.subscription_end_date)
  const now = new Date()
  const remaining = Math.ceil((trialEnd.getTime() - now.getTime()) / (24 * 60 * 60 * 1000))
  return Math.max(0, remaining)
})

const isTrialing = computed(() => user.value?.subscription_status === 'trialing')
const isActive = computed(() => user.value?.subscription_status === 'active')
const isPastDue = computed(() => user.value?.subscription_status === 'past_due')
const isCanceled = computed(() => {
  if (user.value?.subscription_status !== 'canceled') return false
  if (!user.value?.subscription_end_date) return false
  return new Date(user.value.subscription_end_date) > new Date()
})
const hasAccess = computed(() => isActive.value || isTrialing.value || isCanceled.value)
const needsSubscription = computed(() => !hasAccess.value && !isPastDue.value)

onMounted(async () => {
  // Check for payment status in URL
  const paymentStatus = route.query.payment as string
  if (paymentStatus === 'success') {
    showToast('Payment successful! Welcome to Pro.', 'success')
    router.replace({ path: '/pricing' })
  } else if (paymentStatus === 'canceled') {
    showToast('Payment canceled. You can try again anytime.', 'info')
    router.replace({ path: '/pricing' })
  }

  try {
    const [plansData, subData] = await Promise.all([
      api.getPlans(),
      isAuthenticated.value ? api.getSubscription() : Promise.resolve(null)
    ])
    plans.value = plansData
    subscription.value = subData
  } catch (error) {
    console.error('Failed to load plans:', error)
  } finally {
    isLoading.value = false
  }
})

function loginWithGoogle() {
  // Store intent to start trial after login
  sessionStorage.setItem('organizy_after_login', 'start_trial')
  window.location.href = `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/auth/google/login`
}

async function subscribe(plan: PlanInfo) {
  if (!plan.available) return

  if (!isAuthenticated.value) {
    // Prompt to sign in first
    loginWithGoogle()
    return
  }

  processingPlan.value = plan.name
  try {
    const priceId = billingCycle.value === 'yearly' ? plan.price_id_yearly : plan.price_id
    const { checkout_url } = await api.createCheckoutSession(priceId)
    window.location.href = checkout_url
  } catch (error) {
    console.error('Failed to create checkout session:', error)
    showToast('Failed to start checkout. Please try again.', 'error')
  } finally {
    processingPlan.value = null
  }
}

async function manageSubscription() {
  try {
    const { portal_url } = await api.createPortalSession()
    window.location.href = portal_url
  } catch (error) {
    console.error('Failed to open portal:', error)
    showToast('Failed to open billing portal. Please try again.', 'error')
  }
}

function getPrice(plan: PlanInfo) {
  const price = billingCycle.value === 'monthly' ? plan.price_monthly : plan.price_yearly / 12
  return price % 1 === 0 ? price.toString() : price.toFixed(2).replace('.', ',')
}
</script>

<template>
  <div class="pricing-page">
    <!-- Header -->
    <header class="header">
      <RouterLink :to="isAuthenticated ? '/dashboard' : '/'" class="back-link">
        <ArrowLeft :size="20" />
        Back
      </RouterLink>
      <div class="logo">
        <CalendarCheck :size="32" />
        <span>Organizy</span>
      </div>
      <div class="header-spacer"></div>
    </header>

    <!-- Trial Banner -->
    <Alert v-if="isAuthenticated && isTrialing" class="status-banner">
      <Clock class="h-4 w-4 text-[var(--app-text-muted)]" />
      <AlertDescription class="text-[var(--app-text)]">
        <strong>{{ trialDaysRemaining }} days</strong> left in your free trial.
        Your card will be charged after the trial ends.
      </AlertDescription>
    </Alert>

    <!-- Canceled Banner -->
    <Alert v-else-if="isAuthenticated && isCanceled" class="status-banner">
      <Clock class="h-4 w-4 text-orange-400" />
      <AlertDescription class="text-[var(--app-text)]">
        Your subscription is canceled. You still have access until your current period ends. Resubscribe below.
      </AlertDescription>
    </Alert>

    <!-- Past Due Banner -->
    <Alert v-else-if="isAuthenticated && isPastDue" class="status-banner">
      <AlertTriangle class="h-4 w-4 text-red-400" />
      <AlertDescription class="flex items-center gap-3 text-[var(--app-text)]">
        <span><strong>Payment failed.</strong> Please update your payment method to continue.</span>
        <Button size="sm" variant="outline" @click="manageSubscription">
          Update Payment
        </Button>
      </AlertDescription>
    </Alert>

    <!-- Needs subscription Banner (new users or expired) -->
    <Alert v-else-if="isAuthenticated && needsSubscription" class="status-banner">
      <CreditCard class="h-4 w-4 text-[var(--theme-accent)]" />
      <AlertDescription class="text-[var(--app-text)]">
        Start your 7-day free trial to access all features. Cancel anytime.
      </AlertDescription>
    </Alert>

    <!-- Hero -->
    <section class="hero">
      <h1>Unlock all features</h1>
      <p>7-day free trial. Cancel anytime before trial ends.</p>

      <div class="billing-toggle">
        <button
          :class="{ active: billingCycle === 'monthly' }"
          @click="billingCycle = 'monthly'"
        >
          Monthly
        </button>
        <button
          :class="{ active: billingCycle === 'yearly' }"
          @click="billingCycle = 'yearly'"
        >
          Yearly
          <span class="save-badge">Save 33%</span>
        </button>
      </div>
    </section>

    <!-- Plans -->
    <section class="plans">
      <div v-if="isLoading" class="loading">
        <Loader2 :size="32" class="spinner" />
      </div>

      <div v-else class="plans-grid">
        <div
          v-for="plan in plans"
          :key="plan.name"
          :class="['plan-card', { featured: plan.is_popular, unavailable: !plan.available }]"
        >
          <Badge v-if="plan.is_popular" class="absolute -top-3 left-1/2 -translate-x-1/2 bg-stone-600 text-white border-0">
            7 Days Free
          </Badge>
          <Badge v-if="!plan.available" variant="secondary" class="absolute -top-3 left-1/2 -translate-x-1/2">
            Coming Soon
          </Badge>

          <h2 class="plan-name">{{ plan.name }}</h2>

          <div class="plan-price">
            <span class="amount">{{ getPrice(plan) }}</span>
            <span class="currency">€</span>
            <span class="period">/mo</span>
          </div>

          <p v-if="billingCycle === 'yearly' && plan.price_yearly > 0" class="billed-yearly">
            Billed {{ plan.price_yearly.toFixed(2).replace('.', ',') }}€/year
          </p>
          <p v-else-if="plan.price_monthly > 0" class="billed-yearly">
            After 7-day free trial
          </p>

          <ul class="features-list">
            <li v-for="feature in plan.features" :key="feature">
              <Check :size="16" />
              {{ feature }}
            </li>
          </ul>

          <!-- Active subscriber -->
          <Button
            v-if="isActive && plan.is_popular"
            @click="manageSubscription"
            class="plan-button manage"
          >
            Manage Subscription
          </Button>

          <!-- Trialing user -->
          <Button
            v-else-if="isTrialing && plan.is_popular"
            @click="manageSubscription"
            class="plan-button manage"
          >
            Manage Trial
          </Button>

          <!-- Past Due user - needs to update payment -->
          <Button
            v-else-if="isPastDue && plan.is_popular"
            @click="manageSubscription"
            class="plan-button past-due"
          >
            <AlertTriangle :size="16" />
            Update Payment Method
          </Button>

          <!-- Canceled user - can resubscribe -->
          <Button
            v-else-if="isCanceled && plan.is_popular"
            :disabled="processingPlan === plan.name"
            :class="['plan-button', { featured: true }]"
            @click="subscribe(plan)"
          >
            <Loader2 v-if="processingPlan === plan.name" :size="16" class="spinner" />
            <span v-else>Resubscribe</span>
          </Button>

          <!-- New user or expired - start trial -->
          <Button
            v-else
            :disabled="!plan.available || processingPlan === plan.name"
            :class="['plan-button', { featured: plan.is_popular }]"
            @click="subscribe(plan)"
          >
            <Loader2 v-if="processingPlan === plan.name" :size="16" class="spinner" />
            <span v-else>Start Free Trial</span>
          </Button>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="faq">
      <h2>Frequently asked questions</h2>
      <div class="faq-grid">
        <div class="faq-item">
          <h3>How does the free trial work?</h3>
          <p>Enter your card to start a 7-day free trial with full access. Cancel anytime before the trial ends and you won't be charged.</p>
        </div>
        <div class="faq-item">
          <h3>When will I be charged?</h3>
          <p>Your card will be charged after your 7-day trial ends. You'll receive an email reminder before the trial expires.</p>
        </div>
        <div class="faq-item">
          <h3>Can I cancel anytime?</h3>
          <p>Yes! Cancel during the trial and pay nothing. After that, cancel anytime and keep access until your billing period ends.</p>
        </div>
        <div class="faq-item">
          <h3>What payment methods do you accept?</h3>
          <p>We accept all major credit cards through our secure payment processor, Stripe.</p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <p>Questions? Contact us at support@example.com</p>
    </footer>
  </div>
</template>

<style scoped>
.pricing-page {
  min-height: 100vh;
  background: var(--app-bg, #faf8f5);
  color: var(--app-text, #1a1815);
}

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 32px;
  border-bottom: 1px solid var(--app-border);
}

.back-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--app-text-muted);
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.back-link:hover {
  color: var(--app-text);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--theme-accent);
  font-weight: 600;
  font-size: 1.25rem;
}

.header-spacer {
  width: 60px;
}

/* Status banner */
.status-banner {
  display: flex;
  justify-content: center;
  background: var(--app-surface-3);
  border: none;
  border-bottom: 1px solid var(--app-border);
  border-radius: 0;
}

/* Hero */
.hero {
  text-align: center;
  padding: 64px 32px 48px;
}

.hero h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 12px;
}

.hero p {
  font-size: 1.125rem;
  color: var(--app-text-muted);
  margin: 0 0 32px;
}

.billing-toggle {
  display: inline-flex;
  background: var(--app-surface-2);
  border-radius: 8px;
  padding: 4px;
}

.billing-toggle button {
  background: transparent;
  border: none;
  color: var(--app-text-muted);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.billing-toggle button.active {
  background: var(--app-surface-3);
  color: var(--app-text);
}

.save-badge {
  background: var(--theme-accent);
  color: white;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Plans */
.plans {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 32px 64px;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 64px;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.plans-grid {
  display: flex;
  justify-content: center;
  gap: 24px;
}

.plan-card {
  max-width: 380px;
  width: 100%;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 16px;
  padding: 32px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.plan-card.featured {
  border-color: var(--theme-accent);
  background: linear-gradient(180deg, rgba(120, 113, 108, 0.05) 0%, transparent 50%);
}

.plan-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 16px;
}

.plan-price {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;
}

.currency {
  font-size: 1.25rem;
  color: var(--app-text-muted);
}

.amount {
  font-size: 3rem;
  font-weight: 700;
}

.period {
  font-size: 1rem;
  color: var(--app-text-muted);
}

.billed-yearly {
  font-size: 0.875rem;
  color: var(--app-text-muted);
  margin: 0 0 24px;
}

.features-list {
  list-style: none;
  padding: 0;
  margin: 0 0 32px;
  flex: 1;
}

.features-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  font-size: 0.875rem;
  color: var(--app-text-muted);
}

.features-list li svg {
  color: var(--theme-accent);
  flex-shrink: 0;
}

.plan-button {
  width: 100%;
  background: var(--app-surface-3);
  border: none;
  color: var(--app-text);
  padding: 12px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.plan-button:hover:not(:disabled) {
  background: var(--app-border-hover);
}

.plan-button.featured {
  background: var(--theme-accent);
}

.plan-button.featured:hover:not(:disabled) {
  background: var(--theme-accent-hover);
}

.plan-button.manage {
  background: transparent;
  border: 1px solid var(--app-border-hover);
}

.plan-button.past-due {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #fca5a5;
}

.plan-button.past-due:hover {
  background: rgba(239, 68, 68, 0.3);
}

.plan-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* FAQ */
.faq {
  max-width: 900px;
  margin: 0 auto;
  padding: 64px 32px;
  border-top: 1px solid var(--app-border);
}

.faq h2 {
  text-align: center;
  font-size: 1.5rem;
  margin: 0 0 48px;
}

.faq-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
}

.faq-item h3 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 8px;
}

.faq-item p {
  font-size: 0.875rem;
  color: var(--app-text-muted);
  margin: 0;
  line-height: 1.6;
}

/* Footer */
.footer {
  text-align: center;
  padding: 32px;
  border-top: 1px solid var(--app-border);
}

.footer p {
  color: var(--app-text-dim);
  margin: 0;
  font-size: 0.875rem;
}

/* Responsive */
@media (max-width: 700px) {
  .plans-grid {
    grid-template-columns: 1fr;
    max-width: 400px;
    margin: 0 auto;
  }

  .plan-card.featured {
    order: -1;
  }
}

@media (max-width: 640px) {
  .hero h1 {
    font-size: 1.75rem;
  }

  .faq-grid {
    grid-template-columns: 1fr;
  }

  .status-banner {
    flex-direction: column;
    text-align: center;
  }
}
</style>
