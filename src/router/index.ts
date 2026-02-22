import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/pages/HomePage.vue'),
    },
    {
      path: '/oauth/callback',
      name: 'oauth-callback',
      component: () => import('@/pages/OAuthCallbackPage.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/pages/DashboardPage.vue'),
    },
    {
      path: '/daily-tasks',
      name: 'daily-tasks',
      component: () => import('@/pages/DailyTasksPage.vue'),
    },
    {
      path: '/workouts',
      name: 'workouts',
      component: () => import('@/pages/WorkoutsPage.vue'),
    },
    {
      path: '/todos',
      name: 'todos',
      component: () => import('@/pages/TodosPage.vue'),
    },
    {
      path: '/pricing',
      name: 'pricing',
      component: () => import('@/pages/PricingPage.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/pages/SettingsPage.vue'),
    },
  ],
})

export default router
