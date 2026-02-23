import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to) {
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/pages/HomePage.vue'),
      meta: { title: 'Organizy — Organisation personnelle & suivi de régularité' },
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
      meta: { title: 'Tableau de bord — Organizy' },
    },
    {
      path: '/daily-tasks',
      name: 'daily-tasks',
      component: () => import('@/pages/DailyTasksPage.vue'),
      meta: { title: 'Tâches quotidiennes — Organizy' },
    },
    {
      path: '/workouts',
      name: 'workouts',
      component: () => import('@/pages/WorkoutsPage.vue'),
      meta: { title: 'Sport — Organizy' },
    },
    {
      path: '/workouts/presets',
      name: 'workouts-presets',
      component: () => import('@/pages/PresetsPage.vue'),
      meta: { title: 'Presets — Organizy' },
    },
    {
      path: '/todos',
      name: 'todos',
      component: () => import('@/pages/TodosPage.vue'),
      meta: { title: 'Todos — Organizy' },
    },
    {
      path: '/budget',
      name: 'budget',
      component: () => import('@/pages/BudgetPage.vue'),
      meta: { title: 'Budget — Organizy' },
    },
    {
      path: '/pricing',
      name: 'pricing',
      component: () => import('@/pages/PricingPage.vue'),
      meta: { title: 'Tarifs — Organizy' },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/pages/SettingsPage.vue'),
      meta: { title: 'Paramètres — Organizy' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/pages/NotFoundPage.vue'),
      meta: { title: 'Page introuvable — Organizy' },
    },
  ],
})

router.afterEach((to, from) => {
  const title = to.meta.title as string | undefined
  if (title) document.title = title
  if (to.path !== from.path && !to.hash) {
    window.scrollTo({ top: 0, left: 0 })
    document.documentElement.scrollTop = 0
    document.body.scrollTop = 0
  }
})

export default router
