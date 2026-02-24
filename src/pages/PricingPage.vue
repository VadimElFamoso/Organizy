<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/composables/useAuth'
import { Check } from 'lucide-vue-next'

const { isAuthenticated, loginWithGoogle } = useAuth()

const scrolled = ref(false)

function onScroll() {
  scrolled.value = window.scrollY > 10
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

const billingCycle = ref<'monthly' | 'yearly'>('monthly')

interface Plan {
  name: string
  price_monthly: number
  price_yearly: number
  features: string[]
  badge?: string
  highlighted?: boolean
}

const plans: Plan[] = [
  {
    name: 'Gratuit',
    price_monthly: 0,
    price_yearly: 0,
    features: [
      '4 tâches quotidiennes',
      '8 tâches kanban',
      'Historique sport limité à 30 jours',
      'Statistiques de base',
    ],
  },
  {
    name: 'Standard',
    price_monthly: 9.99,
    price_yearly: 83.92,
    badge: 'Populaire',
    highlighted: true,
    features: [
      'Tâches quotidiennes illimitées',
      'Tâches kanban illimitées',
      'Historique sport illimité',
      'Statistiques complètes',
      'Graphique de régularité',
      'Calendrier annuel',
    ],
  },
  {
    name: 'Pro',
    price_monthly: 24.99,
    price_yearly: 209.92,
    features: [
      'Tout le plan Standard',
      'Suivi de budget complet',
      'Graphiques financiers',
      'Gestion des abonnements',
      'Support prioritaire',
    ],
  },
]

function getPrice(plan: Plan) {
  const price = billingCycle.value === 'monthly' ? plan.price_monthly : plan.price_yearly / 12
  if (price === 0) return '0'
  return price % 1 === 0 ? price.toString() : price.toFixed(2).replace('.', ',')
}

function handleCta() {
  if (isAuthenticated.value) {
    window.location.href = '/dashboard'
  } else {
    loginWithGoogle()
  }
}
</script>

<template>
  <div class="page">
    <!-- Nav (same as landing page) -->
    <header class="nav-wrap" :class="{ scrolled }">
      <nav class="nav">
        <RouterLink to="/" class="logo">
          <span class="logo-mark">O</span>
          <span>Organizy</span>
        </RouterLink>
        <div class="nav-center">
          <RouterLink to="/#features">Fonctionnalités</RouterLink>
          <RouterLink to="/#how">Comment ça marche</RouterLink>
          <RouterLink to="/pricing" class="active">Tarifs</RouterLink>
        </div>
        <div class="nav-right">
          <RouterLink v-if="isAuthenticated" to="/dashboard">
            <Button variant="ghost" size="sm">Tableau de bord</Button>
          </RouterLink>
          <Button v-if="!isAuthenticated" size="sm" class="nav-cta" @click="handleLogin">
            Commencer gratuitement
          </Button>
        </div>
      </nav>
    </header>

    <!-- Hero -->
    <section class="hero">
      <h1>Choisissez votre plan</h1>
      <p class="hero-sub">Commencez gratuitement, passez à la vitesse supérieure quand vous voulez.</p>

      <div class="billing-toggle">
        <button
          :class="{ active: billingCycle === 'monthly' }"
          @click="billingCycle = 'monthly'"
        >
          Mensuel
        </button>
        <button
          :class="{ active: billingCycle === 'yearly' }"
          @click="billingCycle = 'yearly'"
        >
          Annuel
          <span class="save-badge">−30 %</span>
        </button>
      </div>
    </section>

    <!-- Plans -->
    <section class="plans">
      <div class="plans-grid">
        <div
          v-for="plan in plans"
          :key="plan.name"
          :class="['plan-card', { featured: plan.highlighted }]"
        >
          <Badge v-if="plan.badge" class="plan-badge featured-badge">
            {{ plan.badge }}
          </Badge>

          <h2 class="plan-name">{{ plan.name }}</h2>

          <div class="plan-price">
            <span class="amount">{{ getPrice(plan) }}</span>
            <span v-if="plan.price_monthly > 0" class="currency">€</span>
            <span class="period">{{ plan.price_monthly === 0 ? '€ pour toujours' : '/mois' }}</span>
          </div>

          <p v-if="billingCycle === 'yearly' && plan.price_yearly > 0" class="billed-yearly">
            Facturé {{ plan.price_yearly.toFixed(2).replace('.', ',') }}€/an
          </p>
          <p v-else-if="plan.price_monthly === 0" class="billed-yearly">
            Aucune carte bancaire requise
          </p>
          <p v-else class="billed-yearly">
            Annulez à tout moment
          </p>

          <ul class="features-list">
            <li v-for="feature in plan.features" :key="feature">
              <Check :size="16" />
              {{ feature }}
            </li>
          </ul>

          <Button
            v-if="plan.price_monthly === 0"
            class="plan-btn"
            @click="handleCta"
          >
            {{ isAuthenticated ? 'Tableau de bord' : 'Commencer gratuitement' }}
          </Button>
          <Button
            v-else
            :class="['plan-btn', { 'plan-btn-primary': plan.highlighted }]"
            @click="handleCta"
          >
            Choisir {{ plan.name }}
          </Button>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="faq">
      <h2>Questions fréquentes</h2>
      <div class="faq-grid">
        <div class="faq-item">
          <h3>Le plan gratuit est-il vraiment gratuit ?</h3>
          <p>Oui, totalement. Pas de carte bancaire, pas d'essai qui expire. Vous pouvez l'utiliser aussi longtemps que vous voulez avec les limites du plan.</p>
        </div>
        <div class="faq-item">
          <h3>Quelles sont les limites du plan gratuit ?</h3>
          <p>Vous pouvez créer jusqu'à 4 tâches quotidiennes et 8 tâches kanban. L'historique sport est conservé 30 jours. Au-delà, les anciennes données sont supprimées automatiquement.</p>
        </div>
        <div class="faq-item">
          <h3>Puis-je annuler à tout moment ?</h3>
          <p>Oui ! Annulez à tout moment et conservez l'accès jusqu'à la fin de votre période de facturation. Repassez au plan gratuit sans rien perdre.</p>
        </div>
        <div class="faq-item">
          <h3>Que comprend le plan Pro ?</h3>
          <p>Tout ce qui est dans le plan Standard, plus l'accès à tous les futurs outils que nous développerons. Vous bénéficiez aussi d'un support prioritaire.</p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-logo">
          <span class="footer-mark">O</span>
          <span>Organizy</span>
        </div>
        <p>Des questions ? Contactez-nous à support@example.com</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--app-bg, #faf8f5);
  color: var(--app-text, #1a1815);
}

/* ── Nav (matches landing page) ── */
.nav-wrap {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--app-bg);
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}

.nav-wrap.scrolled {
  border-bottom-color: var(--app-border);
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1260px;
  margin: 0 auto;
  padding: 12px 40px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--app-text);
  text-decoration: none;
  letter-spacing: -0.02em;
}

.logo-mark {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: var(--app-text);
  color: var(--app-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.85rem;
}

.nav-center {
  display: flex;
  gap: 4px;
}

.nav-center a {
  color: var(--app-text-muted);
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 6px;
  transition: all 0.15s;
}

.nav-center a:hover,
.nav-center a.active {
  color: var(--app-text);
  background: var(--app-surface-2);
}

.nav-right { display: flex; align-items: center; gap: 8px; }
.nav-right a { text-decoration: none; }

.nav-cta {
  padding: 8px 18px;
}

/* ── Hero ── */
.hero {
  text-align: center;
  padding: 64px 32px 48px;
  max-width: 700px;
  margin: 0 auto;
}

.hero h1 {
  font-size: 2.2rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  margin: 0 0 12px;
}

.hero-sub {
  font-size: 1.05rem;
  color: var(--app-text-muted);
  margin: 0 0 32px;
}

.billing-toggle {
  display: inline-flex;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  border-radius: 10px;
  padding: 4px;
}

.billing-toggle button {
  background: transparent;
  border: none;
  color: var(--app-text-muted);
  padding: 8px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.15s;
}

.billing-toggle button.active {
  background: var(--app-surface);
  color: var(--app-text);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.save-badge {
  background: var(--app-text);
  color: var(--app-bg, #faf8f5);
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
}

/* ── Plans ── */
.plans {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 32px 72px;
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
  border-radius: 14px;
  padding: 32px;
  position: relative;
  display: flex;
  flex-direction: column;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.plan-card:hover {
  border-color: var(--app-border-hover);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.plan-card.featured {
  border-color: var(--app-text);
  border-width: 2px;
  transform: scale(1.04);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
}

.plan-card.featured:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.plan-badge {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  white-space: nowrap;
}

.featured-badge {
  background: var(--app-text);
  color: var(--app-bg, #faf8f5);
  border: none;
}

.plan-name {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin: 0 0 16px;
}

.plan-price {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;
}

.currency {
  font-size: 1.15rem;
  color: var(--app-text-muted);
}

.amount {
  font-size: 2.8rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.period {
  font-size: 0.9rem;
  color: var(--app-text-muted);
}

.billed-yearly {
  font-size: 0.8rem;
  color: var(--app-text-muted);
  margin: 0 0 24px;
}

.features-list {
  list-style: none;
  padding: 0;
  margin: 0 0 28px;
  flex: 1;
}

.features-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  font-size: 0.875rem;
  color: var(--app-text-muted);
}

.features-list li svg {
  color: var(--app-text);
  flex-shrink: 0;
}

.plan-btn {
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.plan-btn-primary {
  background: var(--app-text);
  color: var(--app-bg, #faf8f5);
  border: none;
}

.plan-btn-primary:hover:not(:disabled) {
  background: #3d3a36;
}

/* ── FAQ ── */
.faq {
  max-width: 900px;
  margin: 0 auto;
  padding: 64px 32px;
  border-top: 1px solid var(--app-border);
}

.faq h2 {
  text-align: center;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 48px;
}

.faq-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
}

.faq-item {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 24px;
  transition: border-color 0.15s;
}

.faq-item:hover {
  border-color: var(--app-border-hover);
}

.faq-item h3 {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 8px;
}

.faq-item p {
  font-size: 0.85rem;
  color: var(--app-text-muted);
  margin: 0;
  line-height: 1.6;
}

/* ── Footer ── */
.footer {
  border-top: 1px solid var(--app-border);
  padding: 40px 32px;
}

.footer-inner {
  max-width: 1260px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--app-text);
}

.footer-mark {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: var(--app-text);
  color: var(--app-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.72rem;
}

.footer p {
  color: var(--app-text-dim);
  margin: 0;
  font-size: 0.85rem;
}

.footer a {
  color: var(--app-text-muted);
  text-decoration: underline;
  text-underline-offset: 2px;
}

/* ── Responsive ── */
@media (max-width: 1100px) {
  .nav { padding: 12px 24px; }
  .plans { padding: 0 24px 64px; }
  .plans-grid { gap: 20px; }
  .plan-card { max-width: 340px; }
}

@media (max-width: 768px) {
  .nav { padding: 12px 20px; }
  .nav-center { display: none; }

  .hero { padding: 48px 20px 36px; }
  .hero h1 { font-size: 1.6rem; }

  .plans { padding: 0 20px 48px; }
  .plans-grid {
    flex-direction: column;
    align-items: center;
  }

  .plan-card { max-width: 100%; }
  .plan-card.featured { order: -1; transform: none; }

  .faq { padding: 48px 20px; }
  .faq-grid { grid-template-columns: 1fr; }

  .footer-inner {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .hero { padding: 36px 16px 28px; }
  .hero h1 { font-size: 1.4rem; }
  .hero-sub { font-size: 0.92rem; }
  .billing-toggle button { padding: 6px 14px; font-size: 0.8rem; }
  .save-badge { font-size: 0.65rem; padding: 2px 5px; }
  .plans { padding: 0 16px 40px; }
  .plan-card { padding: 24px; }
  .amount { font-size: 2.2rem; }
  .faq { padding: 40px 16px; }
  .faq-item { padding: 18px; }
  .footer { padding: 32px 16px; }
}
</style>
