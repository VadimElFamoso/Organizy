# CLAUDE.md

@CLAUDE.local.md

Always use pnpm for package management.

## Project: Organizy (Personal Organization & Regularity Tracker)

Full-stack personal organization app with Vue 3 frontend + FastAPI backend + PostgreSQL. Companion to Skillzy.

## Language

- **All user-facing text must be in French.** The target audience is French-speaking.
- Backend API responses (error messages, etc.) can stay in English.
- Code, comments, variable names stay in English.

## Core Features

- **Daily Tasks**: Recurring tasks with completion tracking, year dot calendar, regularity graphs
- **Workouts**: Log workouts with type/duration/notes, calendar view, streaks
- **Kanban Todos**: Priority-based boards (Urgent/High/Medium/Low) with drag & drop
- **Dashboard**: Aggregated view of today's tasks, year progression dots, workout summary, top todos
- **Auth**: Google OAuth with httpOnly cookie sessions
- **Payments**: Stripe integration (checkout, portal, webhooks, subscription lifecycle)

## Version 1.0.0 (Current)

Two tiers:
- **Gratuit (Free)**: Restricted access — 4 daily tasks, 8 kanban todos, 30-day workout history, basic stats
- **Standard (9,99€/mois or 83,92€/an — 30% off)**: Full access — unlimited tasks, unlimited kanban, unlimited workout history, full stats, regularity graphs, year calendar

A **Pro** plan (24,99€/mois or 209,92€/an) exists in the pricing page for future advanced features.

## Design System & Style

### Visual Identity
- **Tone**: Warm, calm, minimal. Inspired by Todoist — emotional headlines, two-column hero with product preview, feature blocks with check lists.
- **Typography**: System font stack (`system-ui, -apple-system, sans-serif`). Headlines are bold (700-800 weight) with tight letter-spacing (-0.02 to -0.035em). Body text is 0.88-1rem.
- **Layout**: Max-width 1200px for landing, 1300px for dashboard. Generous padding (80-88px vertical sections).
- **Interactions**: Subtle hover transitions (0.15s). Feature icon boxes scale on hover. Buttons darken.

### Color Palette (CSS variables in `src/App.vue` and `src/style.css`)
```
--app-bg: #faf8f5           warm off-white (page background)
--app-surface: #ffffff       white (cards, product previews)
--app-surface-2: #f5f2ed     light beige (secondary surfaces, testimonial bar)
--app-surface-3: #ebe7e0     darker beige (badges, backgrounds)
--app-border: #e2ddd5        warm gray (borders, dividers)
--app-border-hover: #d4cec5  darker border (hover states, step lines)
--app-text: #1a1815          near-black warm (headlines, primary text, filled dots)
--app-text-muted: #78716c    warm gray (body text, descriptions)
--app-text-dim: #a8a29e      light gray (stats, footnotes, labels)
--theme-accent: #78716c      muted warm gray (icons, logo accent)
--theme-accent-hover: #57534e darker warm gray (button hover, feature text)
```

### Landing Page Pattern (HomePage.vue)
- **Nav**: Logo left, center nav links, CTA button right
- **Hero**: Two-column — emotional headline + subtitle + CTA left, fake product UI (macOS-style window) right
- **Testimonial bar**: Italic quote on beige background
- **Features**: Alternating left/right blocks with tag label, headline, description, checklist, icon box
- **How it works**: 3 numbered steps with connecting lines
- **Bottom CTA**: Dark card (inverted colors) with headline + button
- **Footer**: Logo left, Skillzy link right

### Component Patterns
- All pages use `var(--app-*)` variables — never hardcoded hex in app pages
- Landing page uses scoped styles with hardcoded hex only as fallback
- Dashboard/app pages use `AppNavbar` component
- Cards: `background: var(--app-surface)`, `border: 1px solid var(--app-border)`, `border-radius: 12px`
- Labels: uppercase, 0.68-0.72rem, letter-spacing 0.05-0.06em, `var(--app-text-dim)`

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
- Use CSS variables for all colors — no hardcoded hex in app pages

## Key Backend Models

- `DailyTask` — Recurring tasks per user (soft delete via `is_active`)
- `DailyTaskCompletion` — One per task per day, unique constraint `(task_id, completed_date)`
- `Workout` — Workout log entries with type, date, duration
- `TodoItem` — Kanban items with priority (urgent/high/medium/low) and sort_order

## Known Issues

- **Scroll to top on route change**: Navigating from a hash route (e.g. `/#features`) to another page (e.g. `/pricing`) does not scroll to the top. Vue Router's `scrollBehavior` and `afterEach` with `window.scrollTo(0, 0)` don't work reliably with lazy-loaded routes. Needs manual fix — possibly a `Suspense` wrapper, eager-loading key pages, or handling scroll in the target page's `onMounted`.

## API Routes

- `/api/v1/daily-tasks` — CRUD + toggle completions + stats
- `/api/v1/workouts` — CRUD + summary + calendar + types
- `/api/v1/todos` — CRUD + bulk delete + reorder + top
- `/api/v1/dashboard` — Aggregated dashboard data
