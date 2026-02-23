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
        <h1>Organisez vos journées, sans effort.</h1>
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

      <div class="feat-sections">
        <!-- Habitudes quotidiennes -->
        <div class="feat-section">
          <div class="feat-content">
            <div class="feat-icon-wrap icon-peach">
              <CalendarCheck :size="26" stroke-width="2" />
            </div>
            <h3>Habitudes quotidiennes</h3>
            <p>Définissez vos tâches récurrentes et suivez votre régularité au fil du temps.</p>
          </div>
          <div class="feat-preview">
            <div class="fp-card card-peach-bg">
              <div class="fp-bar">
                <div class="fp-dots"><span /><span /><span /></div>
                <span class="fp-title">Suivi de la semaine</span>
              </div>
              <div class="fp-body">
                <table class="fp-grid">
                  <thead>
                    <tr>
                      <th />
                      <th>Lun</th><th>Mar</th><th>Mer</th><th>Jeu</th><th>Ven</th><th>Sam</th><th>Dim</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="fp-task-name">Routine matinale</td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq" /></td>
                      <td><span class="fp-sq filled" /></td>
                    </tr>
                    <tr>
                      <td class="fp-task-name">Lire 30 min</td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq" /></td>
                    </tr>
                    <tr>
                      <td class="fp-task-name">Méditer</td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq" /></td>
                    </tr>
                    <tr>
                      <td class="fp-task-name">Journaling</td>
                      <td><span class="fp-sq" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq" /></td>
                      <td><span class="fp-sq filled" /></td>
                      <td><span class="fp-sq" /></td>
                      <td><span class="fp-sq filled" /></td>
                    </tr>
                  </tbody>
                </table>
                <div class="fp-summary">18/28 cette semaine</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Suivi sportif -->
        <div class="feat-section reverse">
          <div class="feat-content">
            <div class="feat-icon-wrap icon-blue">
              <Dumbbell :size="26" stroke-width="2" />
            </div>
            <h3>Suivi sportif</h3>
            <p>Enregistrez chaque séance — type, durée, notes. Gardez votre série.</p>
          </div>
          <div class="feat-preview">
            <div class="fp-card card-blue-bg">
              <div class="fp-bar">
                <div class="fp-dots"><span /><span /><span /></div>
                <span class="fp-title">Historique</span>
              </div>
              <div class="fp-body fp-body-workouts">
                <div class="fp-wo-session">
                  <div class="fp-wo-header">
                    <div class="fp-wo-title">Jambes</div>
                    <div class="fp-wo-info">Lun 17 fév · 45 min</div>
                  </div>
                  <div class="fp-wo-exercises">
                    <div class="fp-wo-ex"><span class="fp-wo-name">Squats</span><span class="fp-wo-detail">4 × 12</span></div>
                    <div class="fp-wo-ex"><span class="fp-wo-name">Presse</span><span class="fp-wo-detail">3 × 10</span></div>
                    <div class="fp-wo-ex"><span class="fp-wo-name">Extensions</span><span class="fp-wo-detail">3 × 15</span></div>
                  </div>
                </div>
                <div class="fp-workout-stats">
                  <span>5 j. consécutifs</span>
                  <span>12 séances</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Todos kanban -->
        <div class="feat-section">
          <div class="feat-content">
            <div class="feat-icon-wrap icon-green">
              <ListTodo :size="26" stroke-width="2" />
            </div>
            <h3>Todos kanban</h3>
            <p>Quatre colonnes de priorité avec glisser-déposer. Simple et efficace.</p>
          </div>
          <div class="feat-preview">
            <div class="fp-card card-green-bg">
              <div class="fp-bar">
                <div class="fp-dots"><span /><span /><span /></div>
                <span class="fp-title">Kanban</span>
              </div>
              <div class="fp-body">
                <div class="fp-kanban">
                  <div class="fp-col">
                    <div class="fp-col-header">
                      <span class="fp-dot dot-light" />
                      <span>Basse</span>
                      <span class="fp-count">2</span>
                    </div>
                    <div class="fp-mini-card">Refactorer utils</div>
                    <div class="fp-mini-card">Nettoyer les logs</div>
                  </div>
                  <div class="fp-col">
                    <div class="fp-col-header">
                      <span class="fp-dot dot-gray" />
                      <span>Moyenne</span>
                      <span class="fp-count">2</span>
                    </div>
                    <div class="fp-mini-card">Mettre à jour le README</div>
                    <div class="fp-mini-card">Ajouter les tests unitaires</div>
                  </div>
                  <div class="fp-col">
                    <div class="fp-col-header">
                      <span class="fp-dot dot-orange" />
                      <span>Haute</span>
                      <span class="fp-count">3</span>
                    </div>
                    <div class="fp-mini-card">Finir la page prix</div>
                    <div class="fp-mini-card">Revoir les tests</div>
                    <div class="fp-mini-card">Optimiser les requêtes</div>
                  </div>
                  <div class="fp-col">
                    <div class="fp-col-header">
                      <span class="fp-dot dot-red" />
                      <span>Urgent</span>
                      <span class="fp-count">2</span>
                    </div>
                    <div class="fp-mini-card">Corriger le bug login</div>
                    <div class="fp-mini-card">Déployer le hotfix</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Vue d'ensemble -->
        <div class="feat-section reverse">
          <div class="feat-content">
            <div class="feat-icon-wrap icon-amber">
              <LayoutDashboard :size="26" stroke-width="2" />
            </div>
            <h3>Vue d'ensemble</h3>
            <p>Tâches du jour, séries sportives et priorités — un seul coup d'œil.</p>
          </div>
          <div class="feat-preview">
            <div class="fp-card card-amber-bg">
              <div class="fp-bar">
                <div class="fp-dots"><span /><span /><span /></div>
                <span class="fp-title">Tableau de bord</span>
              </div>
              <div class="fp-body">
                <div class="fp-dashboard">
                  <div class="fp-dash-left">
                    <div class="fp-dash-label">Tâches du jour</div>
                    <div class="fp-dash-task"><span class="fp-check done" />Routine matinale</div>
                    <div class="fp-dash-task"><span class="fp-check done" />Lire 30 min</div>
                    <div class="fp-dash-task"><span class="fp-check" />Méditer</div>
                    <div class="fp-dash-progress">
                      <div class="fp-dash-track"><div class="fp-dash-fill" style="width: 66%" /></div>
                      <span>2/3</span>
                    </div>
                  </div>
                  <div class="fp-dash-right">
                    <div class="fp-dash-mini">
                      <div class="fp-dash-label">Régularité</div>
                      <svg class="fp-sparkline" viewBox="0 0 120 32" fill="none">
                        <path d="M0,20 C10,22 18,26 28,24 C38,22 42,12 52,10 C62,8 67,20 77,22 C87,24 92,10 102,8 C112,6 118,16 120,18" stroke="#1a1815" stroke-width="1.5" stroke-linecap="round" fill="none" />
                      </svg>
                    </div>
                    <div class="fp-dash-mini">
                      <div class="fp-dash-label">Série</div>
                      <div class="fp-dash-big">12</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
  padding: 88px 40px 96px;
  text-align: center;
  display: flex;
  justify-content: center;
}

.hero-inner {
  max-width: 800px;
}

.hero-inner h1 {
  font-size: 4.2rem;
  font-weight: 800;
  line-height: 1.08;
  letter-spacing: -0.04em;
  margin: 0 0 28px;
}

.hero-sub {
  font-size: 1.2rem;
  color: var(--app-text-muted);
  line-height: 1.65;
  margin: 0 auto 36px;
  max-width: 520px;
}

.hero-ctas {
  display: flex;
  justify-content: center;
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

.feat-sections {
  display: flex;
  flex-direction: column;
  gap: 80px;
}

.feat-section {
  display: flex;
  align-items: center;
  gap: 56px;
}

.feat-section.reverse {
  flex-direction: row-reverse;
}

.feat-content {
  flex: 1;
  min-width: 0;
}

.feat-preview {
  flex: 1.2;
  min-width: 0;
}

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

.feat-content h3 {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0 0 12px;
  letter-spacing: -0.02em;
  color: var(--app-text);
}

.feat-content p {
  color: #57534e;
  line-height: 1.6;
  margin: 0;
  font-size: 1.05rem;
  max-width: 380px;
}

/* ── Feature previews ── */
.fp-card {
  background: #ffffff;
  border: 1px solid #e2ddd5;
  border-radius: 14px;
  overflow: hidden;
  box-shadow:
    0 1px 3px rgba(0,0,0,0.04),
    0 8px 28px rgba(0,0,0,0.07),
    0 20px 50px rgba(0,0,0,0.04);
  transition: transform 0.25s ease;
}

.fp-card:hover {
  transform: translateY(-6px);
}

.card-peach-bg  { border-color: #f5d0bc; }
.card-blue-bg   { border-color: #b8c9f5; }
.card-green-bg  { border-color: #a3e8b8; }
.card-amber-bg  { border-color: #f0d87a; }

.fp-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f2ed;
  border-bottom: 1px solid #e2ddd5;
}

.fp-dots {
  display: flex;
  gap: 4px;
}

.fp-dots span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.fp-dots span:nth-child(1) { background: #fca5a5; }
.fp-dots span:nth-child(2) { background: #fcd34d; }
.fp-dots span:nth-child(3) { background: #86efac; }

.fp-title {
  font-size: 0.65rem;
  font-weight: 500;
  color: #78716c;
}

.fp-body {
  padding: 14px;
}

/* Card 1 — Weekly grid */
.fp-grid {
  width: 100%;
  border-collapse: collapse;
}

.fp-grid th {
  font-weight: 500;
  color: #a8a29e;
  padding: 0 0 6px;
  text-align: center;
  font-size: 0.6rem;
}

.fp-grid td {
  padding: 3px;
  text-align: center;
}

.fp-task-name {
  text-align: left !important;
  font-weight: 500;
  color: #1a1815;
  white-space: nowrap;
  padding-right: 8px !important;
  font-size: 0.7rem;
}

.fp-sq {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
  background: #ebe7e0;
}

.fp-sq.filled {
  background: #1a1815;
}

.fp-summary {
  margin-top: 8px;
  font-size: 0.68rem;
  color: #a8a29e;
  font-weight: 500;
  text-align: right;
}

/* Card 2 — Workout sessions */
.fp-body-workouts {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.fp-wo-session {
  background: #faf8f5;
  border: 1px solid #e2ddd5;
  border-radius: 8px;
  padding: 12px 14px;
}

.fp-wo-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}

.fp-wo-title {
  font-size: 0.85rem;
  font-weight: 650;
  color: #1a1815;
}

.fp-wo-info {
  font-size: 0.68rem;
  color: #a8a29e;
  font-weight: 500;
}

.fp-wo-exercises {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.fp-wo-ex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.74rem;
  color: #57534e;
  padding: 3px 0;
}

.fp-wo-name {
  font-weight: 450;
}

.fp-wo-detail {
  font-weight: 600;
  color: #1a1815;
  font-size: 0.7rem;
}

.fp-workout-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #f5f2ed;
  font-size: 0.68rem;
  color: #78716c;
  font-weight: 500;
}

/* Card 3 — Kanban */
.fp-kanban {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.fp-col {
  min-width: 0;
}

.fp-col-header {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 8px;
  font-size: 0.7rem;
  font-weight: 600;
  color: #78716c;
}

.fp-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-red { background: #ef4444; }
.dot-orange { background: #f97316; }
.dot-gray { background: #a8a29e; }
.dot-light { background: #d4cec5; }

.fp-count {
  background: #ebe7e0;
  border-radius: 4px;
  padding: 1px 5px;
  font-size: 0.62rem;
  font-weight: 600;
  color: #78716c;
  margin-left: auto;
}

.fp-mini-card {
  background: #faf8f5;
  border: 1px solid #e2ddd5;
  border-radius: 6px;
  padding: 8px 9px;
  font-size: 0.72rem;
  color: #1a1815;
  margin-bottom: 6px;
  font-weight: 450;
  line-height: 1.35;
}

/* Card 4 — Dashboard */
.fp-dashboard {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.fp-dash-label {
  font-size: 0.6rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #a8a29e;
  margin-bottom: 8px;
}

.fp-dash-task {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  font-weight: 450;
  color: #1a1815;
  padding: 2px 0;
}

.fp-check {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  border: 1.5px solid #d4cec5;
  flex-shrink: 0;
}

.fp-check.done {
  background: #1a1815;
  border-color: #1a1815;
}

.fp-dash-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 0.62rem;
  color: #a8a29e;
  font-weight: 500;
}

.fp-dash-track {
  flex: 1;
  height: 3px;
  background: #ebe7e0;
  border-radius: 2px;
  overflow: hidden;
}

.fp-dash-fill {
  height: 100%;
  background: #1a1815;
  border-radius: 2px;
}

.fp-dash-right {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fp-dash-mini {
  background: #f5f2ed;
  border-radius: 8px;
  padding: 10px;
}

.fp-sparkline {
  width: 100%;
  height: 24px;
  margin-bottom: 2px;
}

.fp-dash-big {
  font-size: 1.6rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.03em;
  color: #1a1815;
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

.feat-section:nth-child(1) { animation: fade-up 0.45s ease 0.05s both; }
.feat-section:nth-child(2) { animation: fade-up 0.45s ease 0.12s both; }
.feat-section:nth-child(3) { animation: fade-up 0.45s ease 0.19s both; }
.feat-section:nth-child(4) { animation: fade-up 0.45s ease 0.26s both; }

.step:nth-child(1) { animation: fade-up 0.45s ease 0.05s both; }
.step:nth-child(3) { animation: fade-up 0.45s ease 0.15s both; }
.step:nth-child(5) { animation: fade-up 0.45s ease 0.25s both; }

.bottom-card {
  animation: fade-up 0.5s ease both;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .hero {
    padding: 56px 24px 64px;
  }

  .hero-inner h1 { font-size: 3rem; }

  .feat-section,
  .feat-section.reverse {
    flex-direction: column;
    gap: 28px;
  }

  .feat-sections { gap: 56px; }

  .feat-content p { max-width: 100%; }

  .section-header h2 { font-size: 2.6rem; }
}

@media (max-width: 768px) {
  .nav-center { display: none; }
  .nav { padding: 12px 20px; }

  .hero { padding: 48px 20px 56px; }
  .hero-inner h1 { font-size: 2.4rem; }
  .hero-ctas { flex-direction: column; }
  .hero-sub { font-size: 1.05rem; }

  .fp-kanban { grid-template-columns: repeat(2, 1fr); }

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
  .fp-dashboard { grid-template-columns: 1fr; }
}
</style>
