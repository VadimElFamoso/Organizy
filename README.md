# Organizy

Personal organization & regularity tracking app. A companion to [Skillzy](https://skillzy.app) for building habits and staying on top of things.

## Features

- **Daily Tasks** — Define recurring tasks, track completions, view consistency with line charts and weekly tables
- **Year Dot Calendar** — Visualize your entire year at a glance with completion ratio dots (GitHub-style)
- **Workout Tracking** — Log workouts with type, duration, and notes. Track streaks and view activity on a calendar
- **Kanban Todos** — Organize tasks by priority (Urgent/High/Medium/Low) with drag-and-drop boards
- **Dashboard** — Aggregated overview of today's tasks, year calendar, workout summary, and top todos
- **Google OAuth** — Sign in with Google, secure httpOnly cookie sessions
- **Stripe Payments** — Subscriptions, trials, and billing portal (optional, no features gated)

## Tech Stack

### Frontend
- Vue 3 + TypeScript + Vite
- TailwindCSS + shadcn-vue
- vue-draggable-plus (kanban drag & drop)
- chart.js + vue-chartjs (regularity graphs)

### Backend
- FastAPI + SQLAlchemy 2.0 (async)
- PostgreSQL + Alembic migrations
- Google OAuth + JWT sessions
- Stripe SDK

### Infrastructure
- Docker & Docker Compose
- Traefik (reverse proxy, auto SSL)

## Quick Start

```bash
# Install CLI dependencies
uv sync

# Run setup wizard (generates .env)
uv run launchpad init

# Start development
uv run launchpad dev
```

Visit http://localhost:5173

## CLI Commands

```bash
uv run launchpad dev          # Start local docker-compose
uv run launchpad dev vps      # Start dev on VPS
uv run launchpad prod         # Start production
uv run launchpad down         # Stop all containers
uv run launchpad logs         # Tail logs
uv run launchpad db migrate   # Run alembic migrations
uv run launchpad db reset     # Reset database
uv run launchpad db shell     # Open psql shell
```

## Project Structure

```
organizy/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/       # API routes (auth, daily-tasks, workouts, todos, dashboard)
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── core/         # Auth, middleware, database
│   └── alembic/          # Database migrations
├── src/                  # Vue 3 frontend
│   ├── components/       # UI + feature components
│   ├── composables/      # Vue composables (state management)
│   ├── pages/            # Page components
│   ├── services/         # API client
│   └── router/           # Vue Router
├── cli/                  # CLI tool
└── docker-compose.yml    # Local development
```

## License

MIT
