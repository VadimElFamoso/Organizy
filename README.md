# Launchpad

A modern SaaS starter template with Vue 3, FastAPI, and PostgreSQL.

## Features

- **Authentication**: Google OAuth with secure httpOnly cookie sessions
- **Payments**: Stripe integration with subscriptions, trials, and customer portal
- **User Management**: User profiles, preferences, and analytics
- **Modern Stack**: Vue 3 + TypeScript + TailwindCSS + shadcn-vue
- **API**: FastAPI with async PostgreSQL (SQLAlchemy + asyncpg)
- **CLI**: Developer toolkit for common tasks
- **Docker**: Multi-environment support (local, dev, prod)

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 22+
- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- pnpm

### Setup

```bash
# Clone the repo
git clone <your-repo-url> launchpad
cd launchpad

# Install CLI dependencies
uv sync

# Run setup wizard
uv run launchpad init

# Start development
uv run launchpad dev
```

Visit http://localhost:5173

## CLI Commands

```bash
# Development
uv run launchpad dev          # Start local dev (docker-compose up)
uv run launchpad dev vps      # Start dev on VPS
uv run launchpad dev ps       # Show running containers
uv run launchpad dev build    # Build containers
uv run launchpad dev restart  # Restart containers

# Production
uv run launchpad prod         # Start production environment

# Database
uv run launchpad db migrate   # Run migrations
uv run launchpad db reset     # Reset database (destroys data)
uv run launchpad db revision "message"  # Create new migration
uv run launchpad db downgrade # Rollback migration
uv run launchpad db shell     # Open psql shell

# Other
uv run launchpad down         # Stop all containers
uv run launchpad logs         # Tail logs
uv run launchpad logs backend # Tail specific service
```

## Project Structure

```
launchpad/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/       # API routes (auth, users, payments)
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic
│   │   └── core/         # Auth, middleware, database
│   └── alembic/          # Database migrations
├── src/                  # Vue 3 frontend
│   ├── components/ui/    # shadcn-vue components
│   ├── composables/      # Vue composables
│   ├── pages/            # Page components
│   ├── services/         # API client
│   └── router/           # Vue Router
├── cli/                  # Python CLI tool
│   └── commands/         # CLI subcommands
├── docker-compose.yml    # Local development
├── docker-compose.dev.yml   # VPS dev environment
└── docker-compose.prod.yml  # VPS production
```

## Environment Variables

Create a `.env` file (or run `uv run launchpad init`):

```env
# Environment
ENVIRONMENT=dev

# Database
POSTGRES_PASSWORD=your-password

# Google OAuth
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx

# JWT
JWT_SECRET_KEY=your-secret-key

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_PRO_MONTHLY=price_xxx
STRIPE_PRICE_ID_PRO_YEARLY=price_xxx

# URLs (for VPS)
DOMAIN=your-domain.com
FRONTEND_URL=https://your-domain.com
GOOGLE_REDIRECT_URI=https://your-domain.com/api/v1/auth/google/callback
```

## Tech Stack

### Frontend
- Vue 3 with Composition API
- TypeScript
- Vite
- TailwindCSS
- shadcn-vue (UI components)
- Vue Router

### Backend
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL with asyncpg
- Alembic (migrations)
- Authlib (OAuth)
- Stripe SDK

### Infrastructure
- Docker & Docker Compose
- Traefik (reverse proxy, auto SSL)
- uv (Python package management)
- pnpm (Node package management)

## Development

### Frontend

```bash
# Install a shadcn-vue component
pnpm dlx shadcn-vue@latest add button

# Type check
pnpm vue-tsc --noEmit
```

### Backend

```bash
# Run inside container
docker-compose exec backend uv run alembic revision --autogenerate -m "message"
docker-compose exec backend uv run alembic upgrade head

# Lint
cd backend && uv run ruff check .
```

## Deployment

### VPS Setup

1. Clone to `/opt/launchpad` (prod) and `/opt/launchpad-dev` (dev)
2. Copy `.env` files to each directory
3. Run deployment:

```bash
# Production
cd /opt/launchpad
docker-compose -f docker-compose.prod.yml up -d --build

# Dev (with hot reload)
cd /opt/launchpad-dev
docker-compose -f docker-compose.dev.yml up -d --build
```

## License

MIT
