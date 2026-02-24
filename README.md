Organizy
Appli fer s’organizâ en perso et suivâ la régularité. In compagnon d’Skillzy po fé des habitudes et rester à jour dins ses affaires.

Fonctionnalités
Tâches journalières — Définî des tâch’ qui r’viennent, suivâ ç’qu’a sté fait, et veyî la régularité avô des graphiques en ligne et des tablôs hebdomadaires.

Calendrié à p’tits points d’l’année — Veyî tote l’année d’in cop d’œil avô des points d’ratio d’accomplissement (à la façon GitHub).

Suivi d’entrainement — Notâ les séances avô l’tipe, la durée et des notes. Suivâ les séries (streaks) et veyî l’activité su in calendrié.

Kanban Todos — Organisâ les tâches selon la priorité (Urgent/Haut/Moyen/Bas) avô des tablôs qu’on peut trîmbalâ (drag & drop).

Tableau d’bord — Vue d’ensemb’ d’ârdjoû : tâches du djoû, calendrié d’l’année, résumé des entrainements et tâches principales.

Google OAuth — S’connectâ avô Google, sessions sécurisées avô cookies httpOnly.

Paiements Stripe — Abonnements, périodes d’essai et portail d’facturation (optionnel, gn’a rin d’bloqué dins les fonctions).

Pile technologique

Frontend
Vue 3 + TypeScript + Vite
TailwindCSS + shadcn-vue
vue-draggable-plus (kanban drag & drop)
chart.js + vue-chartjs (graphiques d’régularité)

Backend
FastAPI + SQLAlchemy 2.0 (async)
PostgreSQL + migrations Alembic
Google OAuth + sessions JWT
Stripe SDK

Infrastructure
Docker & Docker Compose
Traefik (reverse proxy, SSL automatique)

Démarrage rapide

# Installâ les dépendances CLI

uv sync

# Lanci l’assistant d’configuration (créé l’fichié .env)

uv run launchpad init

# Démarrâ l’développement

uv run launchpad dev

Allâ su [http://localhost:5173](http://localhost:5173)

Commandes CLI

uv run launchpad dev          # Démarrâ docker-compose en local
uv run launchpad dev vps      # Démarrâ en dev su VPS
uv run launchpad prod         # Démarrâ en production
uv run launchpad down         # Arrêtâ tos les conteneurs
uv run launchpad logs         # Veyî les logs en direct
uv run launchpad db migrate   # Lanci les migrations alembic
uv run launchpad db reset     # Remettre à zéro la base
uv run launchpad db shell     # Ovrî la console psql

Structure du projèt

organizy/
├── backend/              # Backend FastAPI
│   ├── app/
│   │   ├── api/v1/       # Routes API (auth, daily-tasks, workouts, todos, dashboard)
│   │   ├── models/       # Modèles SQLAlchemy
│   │   ├── schemas/      # Schémas Pydantic
│   │   ├── services/     # Logique métier
│   │   └── core/         # Auth, middleware, base de données
│   └── alembic/          # Migrations base de données
├── src/                  # Frontend Vue 3
│   ├── components/       # Composants UI + fonctions
│   ├── composables/      # Composables Vue (gestion d’état)
│   ├── pages/            # Pages
│   ├── services/         # Client API
│   └── router/           # Routeur Vue
├── cli/                  # Outil CLI
└── docker-compose.yml    # Développement local

Licence
MIT
