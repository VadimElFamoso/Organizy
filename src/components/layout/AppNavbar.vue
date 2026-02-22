<script setup lang="ts">
import { ref, toRef } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  LogOut,
  User,
  Menu,
  X,
  Crown,
  Clock,
  Settings,
  ChevronLeft,
  Rocket,
} from 'lucide-vue-next'
import { useSubscription } from '@/composables/useSubscription'
import type { User as UserType } from '@/services/api'

type NavbarMode = 'dashboard' | 'settings'

interface Props {
  mode: NavbarMode
  user: UserType | null
  showBackButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showBackButton: false,
})

const emit = defineEmits<{
  logout: []
  back: []
}>()

const router = useRouter()
const userRef = toRef(props, 'user')
const { isTrialing, isActive, isCanceled, needsSubscription, trialDaysRemaining } = useSubscription(userRef)

const mobileMenuOpen = ref(false)

function handleBack() {
  emit('back')
}

function handleLogout() {
  emit('logout')
}

function goToSettings() {
  router.push('/settings')
}

function handleMobileAction(action: () => void) {
  action()
  mobileMenuOpen.value = false
}
</script>

<template>
  <header class="app-navbar">
    <!-- Left section -->
    <div class="navbar-left">
      <!-- Back button -->
      <button
        v-if="showBackButton"
        class="back-btn"
        @click="handleBack"
      >
        <ChevronLeft :size="18" />
      </button>

      <!-- Logo -->
      <RouterLink to="/dashboard" class="app-navbar-logo">
        <Rocket :size="18" />
        <span class="logo-text">Launchpad</span>
      </RouterLink>
    </div>

    <!-- Right section -->
    <div class="navbar-right">
      <template v-if="user">
        <!-- Subscription badge (desktop) -->
        <RouterLink v-if="isTrialing" to="/settings" class="desktop-only">
          <Badge variant="outline" class="app-navbar-status-badge trialing">
            <Clock :size="12" />
            {{ trialDaysRemaining }}d trial
          </Badge>
        </RouterLink>
        <RouterLink v-else-if="isCanceled" to="/settings" class="desktop-only">
          <Badge variant="outline" class="app-navbar-status-badge canceled">
            <Clock :size="12" />
            {{ trialDaysRemaining }}d left
          </Badge>
        </RouterLink>
        <RouterLink v-else-if="needsSubscription" to="/pricing" class="desktop-only">
          <Badge variant="destructive" class="app-navbar-status-badge needs-sub">
            Start Trial
          </Badge>
        </RouterLink>
        <Badge v-else-if="isActive" variant="outline" class="desktop-only app-navbar-status-badge active">
          <Crown :size="12" />
          Pro
        </Badge>

        <!-- User dropdown (desktop) -->
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <button class="user-menu-trigger desktop-only">
              <img v-if="user?.picture" :src="user.picture" :alt="user?.name" class="app-navbar-user-avatar" />
              <div v-else class="user-avatar-placeholder">
                {{ user?.name?.charAt(0) || '?' }}
              </div>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" class="user-dropdown">
            <div class="user-info">
              <span class="user-name">{{ user?.name }}</span>
              <span class="user-email">{{ user?.email }}</span>
            </div>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              :class="{ 'active-menu-item': mode === 'settings' }"
              @click="goToSettings"
            >
              <Settings :size="16" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem @click="handleLogout" data-variant="destructive">
              <LogOut :size="16" />
              Sign Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </template>

      <!-- Mobile menu toggle -->
      <button class="mobile-menu-btn mobile-only" @click="mobileMenuOpen = !mobileMenuOpen">
        <X v-if="mobileMenuOpen" :size="24" />
        <Menu v-else :size="24" />
      </button>
    </div>

    <!-- Mobile menu overlay -->
    <Transition name="mobile-menu">
      <div v-if="mobileMenuOpen" class="mobile-menu">
        <!-- Navigation -->
        <div class="mobile-menu-section">
          <span class="mobile-section-label">Navigation</span>
          <RouterLink to="/dashboard" class="mobile-menu-item" @click="mobileMenuOpen = false">
            <Rocket :size="18" />
            <span>Dashboard</span>
          </RouterLink>
          <RouterLink to="/pricing" class="mobile-menu-item" @click="mobileMenuOpen = false">
            <Crown :size="18" />
            <span>Pricing</span>
          </RouterLink>
        </div>

        <!-- Auth section (mobile) -->
        <div class="mobile-menu-section mobile-auth-section">
          <template v-if="user">
            <div class="mobile-user-info">
              <img v-if="user.picture" :src="user.picture" :alt="user.name" class="mobile-user-avatar" />
              <User v-else :size="20" class="mobile-user-icon" />
              <div class="mobile-user-details">
                <span class="mobile-user-name">{{ user.name }}</span>
                <span class="mobile-user-email">{{ user.email }}</span>
                <Badge v-if="isTrialing" variant="outline" class="mt-1 app-navbar-status-badge trialing mobile">
                  <Clock :size="10" />
                  {{ trialDaysRemaining }}d trial
                </Badge>
                <Badge v-else-if="isCanceled" variant="outline" class="mt-1 app-navbar-status-badge canceled mobile">
                  <Clock :size="10" />
                  {{ trialDaysRemaining }}d left
                </Badge>
                <Badge v-else-if="needsSubscription" variant="destructive" class="mt-1 app-navbar-status-badge needs-sub mobile">
                  Start Trial
                </Badge>
                <Badge v-else-if="isActive" variant="outline" class="mt-1 app-navbar-status-badge active mobile">
                  <Crown :size="10" />
                  Pro
                </Badge>
              </div>
            </div>
            <RouterLink to="/settings" class="mobile-menu-item" @click="mobileMenuOpen = false">
              <Settings :size="18" />
              <span>Account Settings</span>
            </RouterLink>
            <button class="mobile-menu-item mobile-logout" @click="handleMobileAction(() => emit('logout'))">
              <LogOut :size="18" />
              <span>Sign Out</span>
            </button>
          </template>
        </div>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
.navbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--app-text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.back-btn:hover {
  background: var(--app-surface-3);
  color: var(--app-text);
}

.logo-text {
  font-weight: 600;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-menu-trigger {
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: 50%;
  transition: box-shadow 0.2s;
}

.user-menu-trigger:hover {
  box-shadow: 0 0 0 2px var(--theme-accent);
}

.user-avatar-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--app-surface-3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--app-text-muted);
}

.user-dropdown {
  min-width: 200px;
}

.user-info {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--app-text);
}

.user-email {
  font-size: 0.8rem;
  color: var(--app-text-muted);
}

.active-menu-item {
  background: var(--app-surface-3);
}

/* Mobile menu button */
.mobile-menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--app-text);
  cursor: pointer;
  transition: background 0.15s;
}

.mobile-menu-btn:hover {
  background: var(--app-surface-3);
}

/* Mobile menu overlay */
.mobile-menu {
  position: absolute;
  top: 52px;
  left: 0;
  right: 0;
  background: var(--app-surface-2);
  border-bottom: 1px solid var(--app-border);
  z-index: 1000;
  max-height: calc(100vh - 52px);
  overflow-x: hidden;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  padding-bottom: env(safe-area-inset-bottom, 16px);
}

.mobile-menu-section {
  padding: 8px 0;
  border-bottom: 1px solid var(--app-border);
  overflow: hidden;
}

.mobile-section-label {
  display: block;
  font-size: 0.7rem;
  color: var(--app-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0 16px 8px;
}

.mobile-menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 16px;
  min-height: 52px;
  background: transparent;
  border: none;
  color: var(--app-text);
  font-size: 0.95rem;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
  text-decoration: none;
}

.mobile-menu-item:hover {
  background: var(--app-surface-3);
}

.mobile-menu-item svg {
  color: var(--app-text-muted);
  flex-shrink: 0;
}

.mobile-auth-section {
  border-bottom: none;
  padding-bottom: 16px;
}

.mobile-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--app-surface-3);
  margin: 0 12px 8px;
  border-radius: 8px;
}

.mobile-user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.mobile-user-icon {
  width: 40px;
  height: 40px;
  padding: 10px;
  background: var(--app-surface);
  border-radius: 50%;
  color: var(--app-text-muted);
}

.mobile-user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mobile-user-name {
  font-weight: 500;
  color: var(--app-text);
}

.mobile-user-email {
  font-size: 0.8rem;
  color: var(--app-text-dim);
}

.mobile-logout {
  color: #ef4444;
}

.mobile-logout svg {
  color: #ef4444;
}

/* Mobile menu animation */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: all 0.2s ease;
}

.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive visibility */
.mobile-only {
  display: none;
}

.desktop-only {
  display: flex;
}

/* Mobile breakpoint */
@media (max-width: 768px) {
  .desktop-only {
    display: none !important;
  }

  .mobile-only {
    display: flex !important;
  }

  .mobile-menu-btn {
    display: flex !important;
  }

  .logo-text {
    display: none;
  }
}
</style>
