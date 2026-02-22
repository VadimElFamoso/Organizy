<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/composables/useAuth'
import {
  Dumbbell,
  ListTodo,
  LayoutDashboard,
  ArrowRight,
  Check,
  CalendarCheck,
} from 'lucide-vue-next'

const { isAuthenticated, loginWithGoogle } = useAuth()

const scrolled = ref(false)

function onScroll() {
  scrolled.value = window.scrollY > 10
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
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
    <!-- Nav -->
    <header class="nav-wrap" :class="{ scrolled }">
      <nav class="nav">
        <a href="#" class="logo" @click.prevent="scrollToTop">
          <span class="logo-mark">O</span>
          <span>Organizy</span>
        </a>
        <div class="nav-center">
          <a href="#features">Fonctionnalités</a>
          <a href="#how">Comment ça marche</a>
          <RouterLink to="/pricing">Tarifs</RouterLink>
        </div>
        <div class="nav-right">
          <RouterLink v-if="isAuthenticated" to="/dashboard">
            <Button variant="ghost" size="sm">Tableau de bord</Button>
          </RouterLink>
          <Button v-if="!isAuthenticated" size="sm" class="nav-cta" @click="loginWithGoogle()">
            Commencer gratuitement
          </Button>
        </div>
      </nav>
    </header>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-badge">
          <span class="badge-dot" />
          Simple par nature
        </div>
        <h1>Organisez vos journées,<br />sans effort.</h1>
        <p class="hero-sub">
          Habitudes, sport et tâches — dans un seul espace clair et rapide.
          Pas de superflu, pas de courbe d'apprentissage. Ouvrez, cochez, avancez.
        </p>
        <div class="hero-ctas">
          <Button size="lg" class="primary-btn" @click="handleCta">
            {{ isAuthenticated ? 'Tableau de bord' : 'Commencer gratuitement' }}
            <ArrowRight :size="18" />
          </Button>
          <Button size="lg" variant="outline" class="outline-btn" as="a" href="#features">
            Découvrir
          </Button>
        </div>
        <p class="hero-note">Gratuit pour toujours. Aucune carte bancaire requise.</p>
      </div>

      <!-- Product preview -->
      <div class="hero-preview">
        <div class="preview-lift">
        <div class="preview-card">
          <div class="preview-bar">
            <div class="bar-dots">
              <span /><span /><span />
            </div>
            <span class="bar-title">Tableau de bord</span>
          </div>
          <div class="preview-body">
            <div class="preview-col-left">
              <div class="preview-label">Tâches du jour</div>
              <div class="preview-task">
                <div class="t-check done" /><span>Routine matinale</span>
              </div>
              <div class="preview-task">
                <div class="t-check done" /><span>Lire 30 min</span>
              </div>
              <div class="preview-task">
                <div class="t-check done" /><span>Sport</span>
              </div>
              <div class="preview-task">
                <div class="t-check" /><span>Bilan du soir</span>
              </div>
              <div class="preview-task">
                <div class="t-check" /><span>Journal</span>
              </div>
              <div class="preview-progress">
                <div class="progress-track">
                  <div class="progress-fill" style="width: 60%" />
                </div>
                <span>3 sur 5 faites</span>
              </div>
            </div>
            <div class="preview-col-right">
              <div class="preview-mini-card">
                <div class="preview-label">Régularité</div>
                <svg class="mini-chart" viewBox="0 0 200 60" fill="none">
                  <defs>
                    <linearGradient id="cf" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="var(--app-text)" stop-opacity="0.12" />
                      <stop offset="100%" stop-color="var(--app-text)" stop-opacity="0" />
                    </linearGradient>
                  </defs>
                  <path d="M0,38 C15,42 25,48 40,44 C55,40 60,22 80,18 C100,14 105,38 120,42 C135,46 145,20 160,14 C175,8 185,28 200,32 L200,60 L0,60Z" fill="url(#cf)" />
                  <path d="M0,38 C15,42 25,48 40,44 C55,40 60,22 80,18 C100,14 105,38 120,42 C135,46 145,20 160,14 C175,8 185,28 200,32" stroke="var(--app-text)" stroke-width="2" stroke-linecap="round" fill="none" />
                </svg>
                <span class="mini-stat">4.2 moy/jour</span>
              </div>
              <div class="preview-mini-card streak-card">
                <div class="preview-label">Série</div>
                <div class="streak-num">12</div>
                <span class="mini-stat">jours d'affilée</span>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
    </section>

    <!-- Logos / trust bar -->
    <section class="trust-bar">
      <p>Conçu pour ceux qui veulent avancer — pas passer une heure à configurer un outil.</p>
    </section>

    <!-- Features -->
    <section id="features" class="features">
      <div class="section-header">
        <h2>Faites plus avec moins</h2>
        <p>Pas de pages, pas de bases de données, pas de courbe d'apprentissage. Quatre outils. Zéro friction.</p>
      </div>

      <div class="feat-grid">
        <div class="feat-card card-peach">
          <div class="feat-icon-wrap icon-peach">
            <CalendarCheck :size="26" stroke-width="2" />
          </div>
          <h3>Habitudes quotidiennes</h3>
          <p>Définissez les tâches à faire chaque jour. Cochez-les. Observez votre régularité grandir au fil du temps.</p>
          <ul class="feat-checks">
            <li><Check :size="16" /> Tâches récurrentes</li>
            <li><Check :size="16" /> Tableau de complétion</li>
            <li><Check :size="16" /> Graphique sur 30 jours</li>
          </ul>
        </div>

        <div class="feat-card card-blue">
          <div class="feat-icon-wrap icon-blue">
            <Dumbbell :size="26" stroke-width="2" />
          </div>
          <h3>Suivi sportif</h3>
          <p>Enregistrez chaque séance avec type, notes et durée. Visualisez vos jours d'entraînement. Gardez votre série.</p>
          <ul class="feat-checks">
            <li><Check :size="16" /> Vue calendrier</li>
            <li><Check :size="16" /> Compteur de série</li>
            <li><Check :size="16" /> Auto-complétion</li>
          </ul>
        </div>

        <div class="feat-card card-green">
          <div class="feat-icon-wrap icon-green">
            <ListTodo :size="26" stroke-width="2" />
          </div>
          <h3>Todos kanban</h3>
          <p>Quatre colonnes de priorité. Glissez-déposez entre elles, cochez, archivez quand c'est fait.</p>
          <ul class="feat-checks">
            <li><Check :size="16" /> Glisser-déposer</li>
            <li><Check :size="16" /> Colonnes par priorité</li>
            <li><Check :size="16" /> Archive des tâches faites</li>
          </ul>
        </div>

        <div class="feat-card card-amber">
          <div class="feat-icon-wrap icon-amber">
            <LayoutDashboard :size="26" stroke-width="2" />
          </div>
          <h3>Vue d'ensemble</h3>
          <p>Tout au même endroit. Tâches du jour, séries sportives, priorités — un seul coup d'œil sur votre journée.</p>
          <ul class="feat-checks">
            <li><Check :size="16" /> Vue agrégée</li>
            <li><Check :size="16" /> Graphique de régularité</li>
            <li><Check :size="16" /> Aperçu instantané</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section id="how" class="how">
      <div class="section-header">
        <h2>Zéro config.<br />Démarrage instant.</h2>
        <p>Connectez-vous et c'est parti. Pas de tutoriel, pas de template à choisir, pas d'onboarding de 20 minutes.</p>
      </div>
      <div class="steps">
        <div class="step">
          <div class="step-num">1</div>
          <h3>Connexion Google</h3>
          <p>Un clic. Pas de formulaire, pas de mot de passe.</p>
        </div>
        <div class="step-line" />
        <div class="step">
          <div class="step-num">2</div>
          <h3>Ajoutez vos tâches</h3>
          <p>Créez les habitudes et todos que vous voulez suivre.</p>
        </div>
        <div class="step-line" />
        <div class="step">
          <div class="step-num">3</div>
          <h3>Revenez chaque jour</h3>
          <p>Cochez vos tâches, enregistrez vos séances, regardez vos séries grandir.</p>
        </div>
      </div>
    </section>

    <!-- Bottom CTA -->
    <section class="bottom-cta">
      <div class="bottom-card">
        <h2>Arrêtez de planifier.<br />Passez à l'action.</h2>
        <p>Gratuit pour toujours. Pas de carte bancaire. Pas d'essai qui expire. Foncez.</p>
        <Button size="lg" class="bottom-btn" @click="handleCta">
          {{ isAuthenticated ? 'Tableau de bord' : 'Commencer gratuitement' }}
          <ArrowRight :size="18" />
        </Button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-logo">
          <span class="footer-mark">O</span>
          <span>Organizy</span>
        </div>
        <p>Un compagnon de <a href="https://skillzy.app" target="_blank">Skillzy</a></p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--app-bg);
  color: var(--app-text);
}

/* ── Nav ── */
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

.nav-center a:hover {
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
  max-width: 1260px;
  margin: 0 auto;
  padding: 72px 40px 80px;
  display: flex;
  align-items: center;
  gap: 64px;
}

.hero-inner { flex: 1; }

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px 5px 8px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 100px;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--app-text-muted);
  margin-bottom: 28px;
}

.badge-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.hero-inner h1 {
  font-size: 3.6rem;
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -0.04em;
  margin: 0 0 28px;
}

.hero-sub {
  font-size: 1.2rem;
  color: var(--app-text-muted);
  line-height: 1.65;
  margin: 0 0 36px;
  max-width: 480px;
}

.hero-ctas {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}

.hero-note {
  font-size: 0.82rem;
  color: var(--app-text-dim);
  margin: 0;
}

/* ── Buttons ── */
.primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  padding: 14px 28px;
}

.outline-btn {
  font-size: 1rem;
  padding: 14px 28px;
}

/* ── Product preview ── */
.hero-preview {
  flex: 1;
  max-width: 480px;
  min-width: 0;
}

.preview-card {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 14px;
  overflow: hidden;
  box-shadow:
    0 1px 3px rgba(0,0,0,0.04),
    0 8px 28px rgba(0,0,0,0.07),
    0 20px 50px rgba(0,0,0,0.04);

}

.preview-lift {
  transition: transform 0.25s ease;
}

.preview-lift:hover {
  transform: translateY(-8px);
}

.preview-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: var(--app-surface-2);
  border-bottom: 1px solid var(--app-border);
}

.bar-dots {
  display: flex;
  gap: 5px;
}

.bar-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.bar-dots span:nth-child(1) { background: #fca5a5; }
.bar-dots span:nth-child(2) { background: #fcd34d; }
.bar-dots span:nth-child(3) { background: #86efac; }

.bar-title {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--app-text-muted);
}

.preview-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 18px;
}

.preview-label {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--app-text-dim);
  margin-bottom: 10px;
}

.preview-task {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 0.84rem;
  font-weight: 450;
}

.t-check {
  width: 15px;
  height: 15px;
  border-radius: 4px;
  border: 1.5px solid var(--app-border-hover);
  flex-shrink: 0;
}

.t-check.done {
  background: var(--app-text);
  border-color: var(--app-text);
}

.preview-progress {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.7rem;
  color: var(--app-text-dim);
  font-weight: 500;
}

.progress-track {
  flex: 1;
  height: 4px;
  background: var(--app-surface-3);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--app-text);
  border-radius: 2px;
}

.preview-mini-card {
  background: var(--app-surface-2);
  border-radius: 10px;
  padding: 14px;
}

.mini-chart {
  width: 100%;
  height: 44px;
  margin-bottom: 6px;
}

.mini-stat {
  font-size: 0.68rem;
  color: var(--app-text-dim);
  font-weight: 500;
}

.streak-card {
  margin-top: 10px;
}

.streak-num {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.03em;
  margin-bottom: 2px;
}

/* ── Trust bar ── */
.trust-bar {
  border-top: 1px solid var(--app-border);
  border-bottom: 1px solid var(--app-border);
  padding: 36px 40px;
  text-align: center;
  background: var(--app-surface-2);
}

.trust-bar p {
  max-width: 520px;
  margin: 0 auto;
  font-size: 1.05rem;
  color: var(--app-text-muted);
  font-style: italic;
  line-height: 1.6;
}

/* ── Section header ── */
.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-header h2 {
  font-size: 3.2rem;
  font-weight: 800;
  margin: 0 0 16px;
  letter-spacing: -0.04em;
  line-height: 1.08;
}

.section-header p {
  color: var(--app-text-muted);
  font-size: 1.1rem;
  margin: 0;
}

/* ── Features ── */
.features {
  max-width: 1100px;
  margin: 0 auto;
  padding: 100px 40px;
}

.feat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.feat-card {
  border-radius: 18px;
  padding: 36px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.feat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.card-peach  { background: #fef2ed; }
.card-blue   { background: #eef3ff; }
.card-green  { background: #eefbf2; }
.card-amber  { background: #fef9ec; }

.feat-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.icon-peach  { background: #fddcc8; color: #c2410c; }
.icon-blue   { background: #c7d7fe; color: #1e40af; }
.icon-green  { background: #bbf7d0; color: #166534; }
.icon-amber  { background: #fde68a; color: #92400e; }

.feat-card h3 {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: -0.02em;
  color: var(--app-text);
}

.feat-card p {
  color: #57534e;
  line-height: 1.6;
  margin: 0 0 18px;
  font-size: 0.95rem;
}

.feat-checks {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.feat-checks li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.88rem;
  color: #57534e;
  font-weight: 500;
}

.feat-checks li svg {
  color: var(--app-text);
  flex-shrink: 0;
}

/* ── How ── */
.how {
  padding: 100px 40px;
  background: var(--app-surface-2);
  border-top: 1px solid var(--app-border);
  border-bottom: 1px solid var(--app-border);
}

.steps {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  max-width: 820px;
  margin: 0 auto;
}

.step {
  flex: 1;
  text-align: center;
  padding: 0 24px;
}

.step-num {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--app-text);
  color: var(--app-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.1rem;
  margin: 0 auto 16px;
}

.step h3 {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 6px;
}

.step p {
  color: var(--app-text-muted);
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.5;
}

.step-line {
  width: 48px;
  height: 2px;
  background: var(--app-border-hover);
  margin-top: 24px;
  flex-shrink: 0;
}

/* ── Bottom CTA ── */
.bottom-cta {
  padding: 56px 40px 100px;
}

.bottom-card {
  max-width: 760px;
  margin: 0 auto;
  text-align: center;
  background: var(--app-text);
  color: var(--app-bg);
  border-radius: 24px;
  padding: 72px 56px;
  position: relative;
  overflow: hidden;
}

.bottom-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(250, 248, 245, 0.05) 1px, transparent 1px);
  background-size: 22px 22px;
  pointer-events: none;
}

.bottom-card h2 {
  position: relative;
  font-size: 2.8rem;
  font-weight: 800;
  margin: 0 0 14px;
  letter-spacing: -0.035em;
  line-height: 1.1;
}

.bottom-card p {
  position: relative;
  color: rgba(250, 248, 245, 0.5);
  font-size: 1.05rem;
  margin: 0 0 32px;
}

.bottom-btn {
  position: relative;
  background: var(--app-bg) !important;
  color: var(--app-text) !important;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  padding: 14px 32px;
  border-radius: 12px;
}
.bottom-btn:hover { opacity: 0.9 !important; }

/* ── Footer ── */
.footer {
  border-top: 1px solid var(--app-border);
  padding: 28px 40px;
}

.footer-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.88rem;
}

.footer-mark {
  width: 22px;
  height: 22px;
  border-radius: 5px;
  background: var(--app-text);
  color: var(--app-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.65rem;
}

.footer p {
  color: var(--app-text-dim);
  font-size: 0.82rem;
  margin: 0;
}

.footer a {
  color: var(--theme-accent);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.footer a:hover { color: var(--app-text); }

/* ── Entrance animations ── */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.hero-badge {
  animation: fade-up 0.5s ease both;
}

.hero-inner h1 {
  animation: fade-up 0.5s ease 0.08s both;
}

.hero-sub {
  animation: fade-up 0.5s ease 0.16s both;
}

.hero-ctas {
  animation: fade-up 0.5s ease 0.24s both;
}

.hero-note {
  animation: fade-in 0.5s ease 0.32s both;
}

.preview-card {
  animation: fade-up 0.6s ease 0.2s both;
}

.feat-card:nth-child(1) { animation: fade-up 0.45s ease 0.05s both; }
.feat-card:nth-child(2) { animation: fade-up 0.45s ease 0.12s both; }
.feat-card:nth-child(3) { animation: fade-up 0.45s ease 0.19s both; }
.feat-card:nth-child(4) { animation: fade-up 0.45s ease 0.26s both; }

.step:nth-child(1) { animation: fade-up 0.45s ease 0.05s both; }
.step:nth-child(3) { animation: fade-up 0.45s ease 0.15s both; }
.step:nth-child(5) { animation: fade-up 0.45s ease 0.25s both; }

.bottom-card {
  animation: fade-up 0.5s ease both;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .hero {
    flex-direction: column;
    padding: 48px 24px 56px;
    gap: 40px;
  }

  .hero-inner h1 { font-size: 3rem; }
  .hero-preview { max-width: 100%; }

  .feat-grid { grid-template-columns: 1fr; }

  .section-header h2 { font-size: 2.6rem; }
}

@media (max-width: 768px) {
  .nav-center { display: none; }
  .nav { padding: 12px 20px; }

  .hero { padding: 40px 20px 48px; }
  .hero-inner h1 { font-size: 2.4rem; }
  .hero-ctas { flex-direction: column; }
  .hero-sub { font-size: 1.05rem; }

  .preview-body { grid-template-columns: 1fr; }

  .features { padding: 72px 20px; }
  .how { padding: 72px 20px; }

  .steps {
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }

  .step-line {
    width: 2px;
    height: 24px;
  }

  .bottom-cta { padding: 40px 20px 72px; }
  .bottom-card { padding: 48px 28px; }
  .bottom-card h2 { font-size: 1.8rem; }

  .footer-inner {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .hero-inner h1 { font-size: 2rem; }
  .section-header h2 { font-size: 2rem; }
}
</style>
