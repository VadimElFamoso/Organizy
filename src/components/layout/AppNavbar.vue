<script setup lang="ts">
import { RouterLink, useRouter, useRoute } from 'vue-router'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  LogOut,
  Settings,
  ChevronLeft,
  CalendarCheck,
  LayoutDashboard,
  Dumbbell,
  ListTodo,
  Wallet,
} from 'lucide-vue-next'
import type { User as UserType } from '@/services/api'

type NavbarMode = 'dashboard' | 'settings'

interface Props {
  mode: NavbarMode
  user: UserType | null
  showBackButton?: boolean
}

withDefaults(defineProps<Props>(), {
  showBackButton: false,
})

const emit = defineEmits<{
  logout: []
  back: []
}>()

const router = useRouter()
const route = useRoute()

function handleBack() {
  emit('back')
}

function handleLogout() {
  emit('logout')
}

function goToSettings() {
  router.push('/settings')
}

const navLinks = [
  { to: '/dashboard', label: 'Tableau de bord', icon: LayoutDashboard },
  { to: '/daily-tasks', label: 'Tâches quotidiennes', icon: CalendarCheck },
  { to: '/workouts', label: 'Sport', icon: Dumbbell },
  { to: '/todos', label: 'Tâches', icon: ListTodo },
  { to: '/budget', label: 'Budget', icon: Wallet },
]

const bottomNavLinks = [
  { to: '/dashboard', label: 'Accueil', icon: LayoutDashboard },
  { to: '/daily-tasks', label: 'Tâches', icon: CalendarCheck },
  { to: '/workouts', label: 'Sport', icon: Dumbbell },
  { to: '/todos', label: 'Projets', icon: ListTodo },
  { to: '/budget', label: 'Budget', icon: Wallet },
]

function isActive(path: string) {
  if (path === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(path)
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
        <span class="logo-mark">O</span>
        <span class="logo-text">Organizy</span>
      </RouterLink>

      <!-- Nav links (desktop) -->
      <nav class="nav-links desktop-only">
        <RouterLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="nav-link"
          :class="{ active: isActive(link.to) }"
        >
          <component :is="link.icon" :size="16" />
          <span>{{ link.label }}</span>
        </RouterLink>
      </nav>
    </div>

    <!-- Right section -->
    <div class="navbar-right">
      <template v-if="user">
        <!-- User dropdown -->
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <button class="user-menu-trigger">
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
              Paramètres
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem @click="handleLogout" data-variant="destructive">
              <LogOut :size="16" />
              Déconnexion
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </template>
    </div>
  </header>

  <!-- Bottom navigation (mobile) -->
  <nav class="bottom-nav">
    <RouterLink
      v-for="link in bottomNavLinks"
      :key="link.to"
      :to="link.to"
      class="bottom-nav-item"
      :class="{ active: isActive(link.to) }"
    >
      <component :is="link.icon" :size="20" />
      <span>{{ link.label }}</span>
    </RouterLink>
  </nav>
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
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* Nav links */
.nav-links {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-left: 16px;
  padding-left: 16px;
  border-left: 1px solid var(--app-border);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--app-text-muted);
  text-decoration: none;
  transition: all 0.15s;
}

.nav-link:hover {
  background: var(--app-surface-3);
  color: var(--app-text);
}

.nav-link.active {
  background: var(--app-surface-3);
  color: var(--app-text);
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
  box-shadow: 0 0 0 2px var(--app-border-hover);
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

/* Bottom navigation */
.bottom-nav {
  display: none;
}

/* Responsive visibility */
.desktop-only {
  display: flex;
}

/* Mobile breakpoint */
@media (max-width: 768px) {
  .desktop-only {
    display: none !important;
  }

  .logo-text {
    display: none;
  }

  .nav-links {
    display: none;
  }

  .bottom-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 64px;
    padding-bottom: env(safe-area-inset-bottom, 0px);
    z-index: 1000;
    background: var(--app-surface);
    border-top: 1px solid var(--app-border);
    align-items: center;
    justify-content: space-around;
  }

  .bottom-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 8px 0;
    flex: 1;
    text-decoration: none;
    color: var(--app-text-dim);
    transition: color 0.15s;
  }

  .bottom-nav-item span {
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.01em;
  }

  .bottom-nav-item.active {
    color: var(--app-text);
  }

  .bottom-nav-item.active span {
    font-weight: 700;
  }
}
</style>
