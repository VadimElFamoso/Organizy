# CLAUDE.md

@CLAUDE.local.md

Always use pnpm for package management.

## Project: Organizy (Personal Organization & Regularity Tracker)

Full-stack personal organization app with Vue 3 frontend + FastAPI backend + PostgreSQL. Companion to Skillzy.

## Core Features

- **Daily Tasks**: Recurring tasks with completion tracking, year dot calendar, regularity graphs
- **Workouts**: Log workouts with type/duration/notes, calendar view, streaks
- **Kanban Todos**: Priority-based boards (Urgent/High/Medium/Low) with drag & drop
- **Dashboard**: Aggregated view of today's tasks, year calendar, workout summary, top todos
- **Auth**: Google OAuth with httpOnly cookie sessions
- **Payments**: Stripe (in codebase but no features are gated — all users have full access)

## Theme

Light beige/white/gray palette. CSS variables defined in `src/App.vue` and `src/style.css`:
- `--app-bg: #faf8f5` (warm off-white)
- `--app-surface: #ffffff` (white cards)
- `--app-surface-2: #f5f2ed` (light beige)
- `--app-text: #1a1815` (near-black warm)
- `--theme-accent: #78716c` (muted warm gray)

## Local Development

```bash
docker-compose up
# Or separately:
cd backend && uv run uvicorn app.main:app --reload --port 8000
pnpm dev  # frontend on :5173
```

## CLI Tool

```bash
uv sync
uv run launchpad init         # Setup wizard
uv run launchpad dev          # Start local docker-compose
uv run launchpad db migrate   # Run alembic migrations
uv run launchpad db reset     # Reset database
```

## Architecture

- **Frontend**: Vue 3 + Vite + TypeScript + TailwindCSS + shadcn-vue
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Auth**: Google OAuth with JWT
- **Drag & Drop**: vue-draggable-plus
- **Charts**: chart.js + vue-chartjs

## Frontend Guidelines

- **Always use shadcn-vue components** when possible (Button, Badge, Input, etc.)
- Install new components: `pnpm dlx shadcn-vue@latest add <component>`
- Components are in `src/components/ui/`
- **NEVER modify files in `src/components/ui/`** - these are shadcn-vue components
- Prefer shadcn styling over custom CSS

## Key Backend Models

- `DailyTask` — Recurring tasks per user (soft delete via `is_active`)
- `DailyTaskCompletion` — One per task per day, unique constraint `(task_id, completed_date)`
- `Workout` — Workout log entries with type, date, duration
- `TodoItem` — Kanban items with priority (urgent/high/medium/low) and sort_order

## API Routes

- `/api/v1/daily-tasks` — CRUD + toggle completions + stats
- `/api/v1/workouts` — CRUD + summary + calendar + types
- `/api/v1/todos` — CRUD + bulk delete + reorder + top
- `/api/v1/dashboard` — Aggregated dashboard data
