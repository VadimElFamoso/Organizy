<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import { useSubscription } from '@/composables/useSubscription'
import { api, type SubscriptionInfo } from '@/services/api'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import {
  User,
  CreditCard,
  Clock,
  Calendar,
  Crown,
  Loader2,
  ExternalLink,
  LogOut,
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const { user, isAuthenticated, logout } = useAuth()
const { showToast } = useToast()
const {
  isTrialing,
  isActive,
  isCanceled,
  needsSubscription,
  trialDaysRemaining,
  statusLabel,
  statusColor,
} = useSubscription(user)

const subscription = ref<SubscriptionInfo | null>(null)
const isLoading = ref(true)
const isManaging = ref(false)

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }

  const paymentStatus = route.query.payment as string
  if (paymentStatus === 'success') {
    showToast('Payment successful! Welcome to Pro.', 'success')
    router.replace({ path: '/settings' })
  }

  try {
    subscription.value = await api.getSubscription()
  } catch (error) {
    console.error('Failed to load subscription:', error)
  } finally {
    isLoading.value = false
  }
})

async function manageSubscription() {
  isManaging.value = true
  try {
    const { portal_url } = await api.createPortalSession()
    window.location.href = portal_url
  } catch (error) {
    console.error('Failed to open portal:', error)
    showToast('Failed to open billing portal. Please try again.', 'error')
    isManaging.value = false
  }
}

async function handleLogout() {
  await logout()
  router.push('/')
}

function formatDate(dateString?: string) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>

<template>
  <div class="settings-page">
    <AppNavbar
      mode="settings"
      :user="user"
      show-back-button
      @logout="handleLogout"
      @back="router.push('/dashboard')"
    />

    <main class="content">
      <div v-if="isLoading" class="loading">
        <Loader2 :size="32" class="spinner" />
      </div>

      <div v-else-if="user" class="settings-content">
        <h1>Account Settings</h1>

        <!-- Profile Section -->
        <section class="section">
          <h2>
            <User :size="20" />
            Profile
          </h2>
          <div class="card">
            <div class="profile-info">
              <img
                v-if="user.picture"
                :src="user.picture"
                :alt="user.name"
                class="profile-avatar"
              />
              <div v-else class="profile-avatar-placeholder">
                <User :size="32" />
              </div>
              <div class="profile-details">
                <div class="profile-name">{{ user.name }}</div>
                <div class="profile-email">{{ user.email }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- Subscription Section -->
        <section class="section">
          <h2>
            <CreditCard :size="20" />
            Subscription
          </h2>
          <div class="card">
            <div class="subscription-header">
              <div class="subscription-plan">
                <Crown :size="20" class="crown-icon" />
                <span class="plan-name">Pro Plan</span>
                <span :class="['status-badge', statusColor]">{{ statusLabel }}</span>
              </div>
            </div>

            <div v-if="isTrialing" class="subscription-detail">
              <Clock :size="16" />
              <span>
                <strong>{{ trialDaysRemaining }} days</strong> remaining in your trial.
              </span>
            </div>

            <div v-else-if="isCanceled" class="subscription-detail canceled">
              <Clock :size="16" />
              <span>
                Your subscription is canceled. Access ends on <strong>{{ formatDate(user?.subscription_end_date) }}</strong>.
              </span>
            </div>

            <div v-else-if="needsSubscription" class="subscription-detail expired">
              <Clock :size="16" />
              <span>Start a free trial to access all features.</span>
            </div>

            <div v-if="isActive && subscription?.end_date" class="subscription-detail">
              <Calendar :size="16" />
              <span>Renews on {{ formatDate(subscription.end_date) }}</span>
            </div>

            <div class="subscription-actions">
              <Button
                v-if="isActive || isTrialing"
                @click="manageSubscription"
                :disabled="isManaging"
                class="manage-btn"
              >
                <Loader2 v-if="isManaging" :size="16" class="spinner" />
                <ExternalLink v-else :size="16" />
                Manage Subscription
              </Button>

              <RouterLink v-if="needsSubscription || isCanceled" to="/pricing" class="subscribe-link">
                <Button class="subscribe-btn">
                  <Crown :size="16" />
                  {{ isCanceled ? 'Resubscribe' : 'Start Free Trial' }}
                </Button>
              </RouterLink>
            </div>
          </div>
        </section>

        <!-- Session -->
        <section class="section">
          <h2 class="danger-title">
            <LogOut :size="20" />
            Session
          </h2>
          <div class="card">
            <p class="card-description">
              Sign out of your account on this device.
            </p>
            <Button variant="outline" class="logout-btn" @click="handleLogout">
              <LogOut :size="16" />
              Sign Out
            </Button>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.settings-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--app-surface);
  color: var(--app-text);
}

.content {
  max-width: 600px;
  margin: 0 auto;
  padding: 48px 24px;
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

.settings-content h1 {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 32px;
}

.section {
  margin-bottom: 32px;
}

.section h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1rem;
  font-weight: 500;
  color: var(--app-text-dim);
  margin: 0 0 12px;
}

.card {
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 20px;
}

.card-description {
  color: var(--app-text-muted);
  font-size: 0.9rem;
  margin: 0 0 16px;
}

.profile-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-avatar-placeholder {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--app-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--app-text-muted);
}

.profile-name {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 4px;
}

.profile-email {
  font-size: 0.9rem;
  color: var(--app-text-muted);
}

.subscription-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.subscription-plan {
  display: flex;
  align-items: center;
  gap: 10px;
}

.crown-icon {
  color: var(--theme-accent);
}

.plan-name {
  font-size: 1.1rem;
  font-weight: 500;
}

.status-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  text-transform: uppercase;
}

.status-badge.success {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.status-badge.trial {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.status-badge.expired {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.status-badge.canceled {
  background: rgba(251, 146, 60, 0.15);
  color: #fb923c;
}

.status-badge.past_due {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.subscription-detail {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: var(--app-text-dim);
  margin-bottom: 16px;
}

.subscription-detail.expired {
  color: #fca5a5;
}

.subscription-detail.canceled {
  color: #fdba74;
}

.subscription-actions {
  padding-top: 8px;
  border-top: 1px solid var(--app-border);
}

.manage-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: 1px solid var(--app-border-hover);
  color: var(--app-text);
}

.manage-btn:hover:not(:disabled) {
  background: var(--app-border);
}

.subscribe-link {
  text-decoration: none;
}

.subscribe-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--theme-accent);
  border: none;
  color: white;
}

.subscribe-btn:hover {
  opacity: 0.9;
}

.danger-title {
  color: var(--app-text-dim);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  border-color: var(--app-border-hover);
  color: var(--app-text);
}

.logout-btn:hover {
  background: var(--app-border);
  border-color: #52525b;
}

@media (max-width: 768px) {
  .content {
    padding: 32px 16px;
  }
}
</style>
