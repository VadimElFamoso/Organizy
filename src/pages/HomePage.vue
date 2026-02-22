<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/composables/useAuth'
import {
  Rocket,
  Shield,
  CreditCard,
  ArrowRight,
  Zap,
  Code2,
  Database,
  BarChart3,
  Check,
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
        <Rocket :size="20" />
        <span>Launchpad</span>
      </RouterLink>
      <div class="home-navbar-right">
        <RouterLink v-if="isAuthenticated" to="/dashboard">
          <Button size="sm" variant="ghost">Dashboard</Button>
        </RouterLink>
        <RouterLink to="/pricing">
          <Button size="sm" variant="ghost">Pricing</Button>
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
          <Zap :size="14" />
          <span>SaaS Starter Kit</span>
        </div>
        <h1 class="hero-title">
          Ship your SaaS
          <span class="hero-gradient">in days, not months</span>
        </h1>
        <p class="hero-subtitle">
          Authentication, payments, subscriptions, and everything you need to launch your SaaS product. Built with Vue 3, FastAPI, and PostgreSQL.
        </p>
        <div class="hero-actions">
          <Button size="lg" class="primary-btn" @click="handleCta">
            {{ isAuthenticated ? 'Go to Dashboard' : 'Get Started Free' }}
            <ArrowRight :size="20" />
          </Button>
          <RouterLink to="/pricing">
            <Button size="lg" variant="outline" class="secondary-btn">
              View Pricing
            </Button>
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- Features Section -->
    <section class="features">
      <div class="features-header">
        <h2>Everything you need to launch</h2>
        <p>Focus on what makes your product unique. We handle the boring stuff.</p>
      </div>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <Shield :size="24" />
          </div>
          <h3>Authentication</h3>
          <p>Google OAuth with secure httpOnly cookie sessions. Ready to use, production-grade auth.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <CreditCard :size="24" />
          </div>
          <h3>Stripe Payments</h3>
          <p>Multi-tier subscriptions, free trials, promotion codes, and customer portal built-in.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <BarChart3 :size="24" />
          </div>
          <h3>Usage Tracking</h3>
          <p>Per-user monthly usage limits with automatic resets. Enforce tier limits effortlessly.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <Database :size="24" />
          </div>
          <h3>PostgreSQL + Alembic</h3>
          <p>SQLAlchemy async models with Alembic migrations. Schema changes made easy.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <Code2 :size="24" />
          </div>
          <h3>Vue 3 + FastAPI</h3>
          <p>Modern TypeScript frontend with shadcn-vue components. Python backend with auto-generated docs.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <Rocket :size="24" />
          </div>
          <h3>Docker Deploy</h3>
          <p>Multi-environment Docker Compose setup. Local, dev, and production configs included.</p>
        </div>
      </div>
    </section>

    <!-- Included Section -->
    <section class="included">
      <div class="included-content">
        <h2>What's included</h2>
        <div class="included-grid">
          <div class="included-column">
            <div class="included-item"><Check :size="16" /> Google OAuth login</div>
            <div class="included-item"><Check :size="16" /> JWT session management</div>
            <div class="included-item"><Check :size="16" /> Stripe checkout integration</div>
            <div class="included-item"><Check :size="16" /> Multi-tier pricing (Free/Starter/Pro/Unlimited)</div>
            <div class="included-item"><Check :size="16" /> Free trial support</div>
            <div class="included-item"><Check :size="16" /> Customer billing portal</div>
          </div>
          <div class="included-column">
            <div class="included-item"><Check :size="16" /> Monthly usage tracking & limits</div>
            <div class="included-item"><Check :size="16" /> Subscription status banners</div>
            <div class="included-item"><Check :size="16" /> Settings page with profile</div>
            <div class="included-item"><Check :size="16" /> Responsive mobile navigation</div>
            <div class="included-item"><Check :size="16" /> Docker Compose (local/dev/prod)</div>
            <div class="included-item"><Check :size="16" /> Traefik reverse proxy with auto SSL</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <h2>Ready to build?</h2>
      <p>Stop reinventing auth and payments. Start building your product today.</p>
      <Button size="lg" class="primary-btn" @click="handleCta">
        {{ isAuthenticated ? 'Go to Dashboard' : 'Get Started Free' }}
        <ArrowRight :size="20" />
      </Button>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-logo">
          <Rocket :size="16" />
          <span>Launchpad</span>
        </div>
        <p>Built with Vue 3 + FastAPI + PostgreSQL</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--app-surface, #0a0a0b);
  color: var(--app-text, #fafafa);
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
  color: var(--app-text, #fafafa);
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
}

.home-navbar-logo svg {
  color: var(--theme-accent, #ec4899);
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
  background: var(--theme-accent, #ec4899);
  border: none;
  color: white;
  margin-left: 8px;
}

.login-btn:hover {
  background: var(--theme-accent-hover, #db2777);
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
  background: rgba(236, 72, 153, 0.1);
  border: 1px solid rgba(236, 72, 153, 0.2);
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--theme-accent, #ec4899);
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
  background: linear-gradient(135deg, var(--theme-accent, #ec4899), #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: var(--app-text-dim, #a1a1aa);
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
  background: var(--theme-accent, #ec4899);
  border: none;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.primary-btn:hover {
  background: var(--theme-accent-hover, #db2777);
}

.secondary-btn {
  background: transparent;
  border: 1px solid var(--app-border-hover, #3f3f46);
  color: var(--app-text, #fafafa);
}

.secondary-btn:hover {
  background: var(--app-surface-3, #1a1a1c);
}

/* Features */
.features {
  max-width: 1100px;
  margin: 0 auto;
  padding: 80px 32px;
  border-top: 1px solid var(--app-border, #27272a);
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
  color: var(--app-text-muted, #71717a);
  font-size: 1.1rem;
  margin: 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.feature-card {
  padding: 32px;
  background: var(--app-surface-2, #111113);
  border: 1px solid var(--app-border, #27272a);
  border-radius: 12px;
  transition: border-color 0.2s;
}

.feature-card:hover {
  border-color: var(--app-border-hover, #3f3f46);
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  background: rgba(236, 72, 153, 0.1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--theme-accent, #ec4899);
}

.feature-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 8px;
}

.feature-card p {
  color: var(--app-text-muted, #71717a);
  margin: 0;
  line-height: 1.6;
  font-size: 0.9rem;
}

/* Included */
.included {
  border-top: 1px solid var(--app-border, #27272a);
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
  color: var(--app-text-dim, #a1a1aa);
}

.included-item svg {
  color: #22c55e;
  flex-shrink: 0;
}

/* CTA */
.cta {
  text-align: center;
  padding: 80px 32px;
  background: var(--app-surface-2, #111113);
}

.cta h2 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 12px;
}

.cta p {
  color: var(--app-text-muted, #71717a);
  margin: 0 0 32px;
  font-size: 1.1rem;
}

/* Footer */
.footer {
  border-top: 1px solid var(--app-border, #27272a);
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
  color: var(--theme-accent, #ec4899);
}

.footer p {
  color: #52525b;
  margin: 0;
  font-size: 0.85rem;
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
