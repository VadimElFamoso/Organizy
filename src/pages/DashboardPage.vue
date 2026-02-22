<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/composables/useAuth'
import { useSubscription } from '@/composables/useSubscription'
import { SubscriptionBanner } from '@/components'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import { Settings, User } from 'lucide-vue-next'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const { hasAccess, isTrialing, trialDaysRemaining } = useSubscription(user)

onMounted(() => {
  if (!isAuthenticated.value) {
    router.push('/')
  }
})

async function handleLogout() {
  await logout()
  router.push('/')
}
</script>

<template>
  <div class="dashboard-page">
    <AppNavbar mode="dashboard" :user="user" @logout="handleLogout" />
    <SubscriptionBanner />

    <!-- Main Content -->
    <main class="content">
      <div class="welcome-card">
        <div class="welcome-icon">
          <User :size="32" />
        </div>
        <h1>Welcome, {{ user?.name || 'User' }}!</h1>
        <p>Your SaaS starter is ready. Start building your app!</p>

        <div class="status-info">
          <div v-if="hasAccess" class="status-badge success">
            {{ isTrialing ? `Trial: ${trialDaysRemaining} days left` : 'Active Subscription' }}
          </div>
          <div v-else class="status-badge warning">
            <RouterLink to="/pricing">Start your free trial</RouterLink>
          </div>
        </div>

        <div class="quick-links">
          <RouterLink to="/settings">
            <Button variant="outline">
              <Settings :size="16" />
              Account Settings
            </Button>
          </RouterLink>
          <RouterLink to="/pricing">
            <Button variant="outline">
              View Plans
            </Button>
          </RouterLink>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: var(--app-surface);
  color: var(--app-text);
}

.content {
  max-width: 600px;
  margin: 0 auto;
  padding: 64px 24px;
}

.welcome-card {
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  border-radius: 16px;
  padding: 48px;
  text-align: center;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  background: rgba(236, 72, 153, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--theme-accent);
}

.welcome-card h1 {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 12px;
}

.welcome-card p {
  color: var(--app-text-muted);
  margin: 0 0 24px;
}

.status-info {
  margin-bottom: 32px;
}

.status-badge {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-badge.success {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.status-badge.warning {
  background: rgba(251, 146, 60, 0.15);
  color: #fb923c;
}

.status-badge a {
  color: inherit;
  text-decoration: none;
}

.status-badge a:hover {
  text-decoration: underline;
}

.quick-links {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.quick-links a {
  text-decoration: none;
}

.quick-links button {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
