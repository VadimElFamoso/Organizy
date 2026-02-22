<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/composables/useAuth'
import {
  CalendarCheck,
  Dumbbell,
  ListTodo,
  LayoutDashboard,
  ArrowRight,
  Check,
  Sparkles,
} from 'lucide-vue-next'

const { isAuthenticated, loginWithGoogle } = useAuth()

function handleCta() {
  if (isAuthenticated.value) {
    window.location.href = '/dashboard'
  } else {
    loginWithGoogle()
  }
}
</script>

<template>
  <div class="home-page">
    <!-- Navbar -->
    <nav class="home-navbar">
      <RouterLink to="/" class="home-navbar-logo">
        <CalendarCheck :size="20" />
        <span>Organizy</span>
      </RouterLink>
      <div class="home-navbar-right">
        <RouterLink v-if="isAuthenticated" to="/dashboard">
          <Button size="sm" variant="ghost">Dashboard</Button>
        </RouterLink>
        <Button v-if="!isAuthenticated" size="sm" class="login-btn" @click="loginWithGoogle()">
          Sign In
        </Button>
      </div>
    </nav>

    <!-- Hero Section -->
    <header class="hero">
      <div class="hero-content">
        <div class="hero-badge">
          <Sparkles :size="14" />
          <span>Personal Organization</span>
        </div>
        <h1 class="hero-title">
          Stay organized,
          <span class="hero-gradient">build regularity</span>
        </h1>
        <p class="hero-subtitle">
          Track daily tasks, log workouts, organize todos with kanban boards, and visualize your consistency with a year calendar. The perfect complement to Skillzy.
        </p>
        <div class="hero-actions">
          <Button size="lg" class="primary-btn" @click="handleCta">
            {{ isAuthenticated ? 'Go to Dashboard' : 'Get Started Free' }}
            <ArrowRight :size="20" />
          </Button>
        </div>
      </div>
    </header>

    <!-- Features Section -->
    <section class="features">
      <div class="features-header">
        <h2>Everything you need to stay on track</h2>
        <p>Simple tools to build habits, track progress, and get things done.</p>
      </div>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <CalendarCheck :size="24" />
          </div>
          <h3>Daily Tasks</h3>
          <p>Define recurring tasks and track completions. See your consistency over time with graphs and tables.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <Dumbbell :size="24" />
          </div>
          <h3>Workout Tracking</h3>
          <p>Log workouts with type, duration, and notes. View your activity on a calendar and track streaks.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <ListTodo :size="24" />
          </div>
          <h3>Kanban Todos</h3>
          <p>Organize tasks by priority with drag-and-drop kanban boards. Urgent, high, medium, and low columns.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <LayoutDashboard :size="24" />
          </div>
          <h3>Year Calendar</h3>
          <p>Visualize your entire year at a glance with a dot calendar showing daily completion ratios.</p>
        </div>
      </div>
    </section>

    <!-- Included Section -->
    <section class="included">
      <div class="included-content">
        <h2>What you get</h2>
        <div class="included-grid">
          <div class="included-column">
            <div class="included-item"><Check :size="16" /> Recurring daily task management</div>
            <div class="included-item"><Check :size="16" /> Completion tracking with date ranges</div>
            <div class="included-item"><Check :size="16" /> Year dot calendar visualization</div>
            <div class="included-item"><Check :size="16" /> Regularity line charts</div>
          </div>
          <div class="included-column">
            <div class="included-item"><Check :size="16" /> Workout logging with streaks</div>
            <div class="included-item"><Check :size="16" /> Kanban board with drag & drop</div>
            <div class="included-item"><Check :size="16" /> Priority-based todo organization</div>
            <div class="included-item"><Check :size="16" /> Aggregated dashboard overview</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <h2>Ready to get organized?</h2>
      <p>Start tracking your habits and todos today. Free to use, no credit card required.</p>
      <Button size="lg" class="primary-btn" @click="handleCta">
        {{ isAuthenticated ? 'Go to Dashboard' : 'Get Started Free' }}
        <ArrowRight :size="20" />
      </Button>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-logo">
          <CalendarCheck :size="16" />
          <span>Organizy</span>
        </div>
        <p>A companion to <a href="https://skillzy.app" target="_blank" class="skillzy-link">Skillzy</a></p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--app-bg, #faf8f5);
  color: var(--app-text, #1a1815);
}

/* Navbar */
.home-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  max-width: 1200px;
  margin: 0 auto;
}

.home-navbar-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--app-text, #1a1815);
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
}

.home-navbar-logo svg {
  color: var(--theme-accent, #78716c);
}

.home-navbar-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.home-navbar-right a {
  text-decoration: none;
}

.login-btn {
  background: var(--app-text, #1a1815);
  border: none;
  color: white;
  margin-left: 8px;
}

.login-btn:hover {
  background: var(--theme-accent-hover, #57534e);
}

/* Hero */
.hero {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 800px;
  margin: 0 auto;
  padding: 80px 32px 80px;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--app-surface-2, #f5f2ed);
  border: 1px solid var(--app-border, #e2ddd5);
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--theme-accent, #78716c);
  margin-bottom: 24px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.1;
  margin: 0 0 24px;
  letter-spacing: -0.02em;
}

.hero-gradient {
  display: block;
  background: linear-gradient(135deg, #57534e, #a8a29e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: var(--app-text-muted, #78716c);
  margin: 0 0 40px;
  line-height: 1.6;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.primary-btn {
  background: var(--app-text, #1a1815);
  border: none;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.primary-btn:hover {
  background: var(--theme-accent-hover, #57534e);
}

/* Features */
.features {
  max-width: 1100px;
  margin: 0 auto;
  padding: 80px 32px;
  border-top: 1px solid var(--app-border, #e2ddd5);
}

.features-header {
  text-align: center;
  margin-bottom: 48px;
}

.features-header h2 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 12px;
}

.features-header p {
  color: var(--app-text-muted, #78716c);
  font-size: 1.1rem;
  margin: 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.feature-card {
  padding: 32px;
  background: var(--app-surface, #ffffff);
  border: 1px solid var(--app-border, #e2ddd5);
  border-radius: 12px;
  transition: border-color 0.2s;
}

.feature-card:hover {
  border-color: var(--app-border-hover, #d4cec5);
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  background: var(--app-surface-2, #f5f2ed);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--theme-accent, #78716c);
}

.feature-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 8px;
}

.feature-card p {
  color: var(--app-text-muted, #78716c);
  margin: 0;
  line-height: 1.6;
  font-size: 0.9rem;
}

/* Included */
.included {
  border-top: 1px solid var(--app-border, #e2ddd5);
  padding: 80px 32px;
}

.included-content {
  max-width: 800px;
  margin: 0 auto;
}

.included h2 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 32px;
  text-align: center;
}

.included-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 48px;
}

.included-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  font-size: 0.95rem;
  color: var(--app-text-muted, #78716c);
}

.included-item svg {
  color: #16a34a;
  flex-shrink: 0;
}

/* CTA */
.cta {
  text-align: center;
  padding: 80px 32px;
  background: var(--app-surface-2, #f5f2ed);
}

.cta h2 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 12px;
}

.cta p {
  color: var(--app-text-muted, #78716c);
  margin: 0 0 32px;
  font-size: 1.1rem;
}

/* Footer */
.footer {
  border-top: 1px solid var(--app-border, #e2ddd5);
  padding: 32px;
}

.footer-content {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  font-size: 0.9rem;
}

.footer-logo svg {
  color: var(--theme-accent, #78716c);
}

.footer p {
  color: var(--app-text-dim, #a8a29e);
  margin: 0;
  font-size: 0.85rem;
}

.skillzy-link {
  color: var(--theme-accent, #78716c);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.skillzy-link:hover {
  color: var(--app-text, #1a1815);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.25rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .included-grid {
    grid-template-columns: 1fr;
  }

  .home-navbar {
    padding: 12px 16px;
  }

  .footer-content {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .hero {
    padding: 48px 16px 64px;
  }

  .hero-title {
    font-size: 1.75rem;
  }

  .home-navbar-right button span {
    display: none;
  }
}
</style>
