# CLAUDE.md

@CLAUDE.local.md

Always use pnpm for package management.

## Project: Launchpad (SaaS Starter)

Full-stack SaaS starter with Vue 3 frontend + FastAPI backend + PostgreSQL.

## Features

- **Authentication**: Google OAuth with httpOnly cookie sessions
- **Payments**: Stripe subscriptions with trials and customer portal
- **User Management**: Profile, preferences, analytics

## Local Development

```bash
# Start everything with Docker
docker-compose up

# Or run separately:
cd backend && uv run uvicorn app.main:app --reload --port 8000
pnpm dev  # frontend on :5173
```

## CLI Tool

```bash
# Install CLI
uv sync

# Setup wizard (generates .env files)
uv run launchpad init

# Development commands
uv run launchpad dev          # Start local docker-compose
uv run launchpad dev vps      # Start dev environment on VPS
uv run launchpad prod         # Start production on VPS
uv run launchpad down         # Stop all containers
uv run launchpad logs         # Tail logs

# Database commands
uv run launchpad db migrate   # Run alembic migrations
uv run launchpad db reset     # Reset database
uv run launchpad db shell     # Open psql shell
```

## Environment Variables (.env)

Required variables:
```
POSTGRES_PASSWORD=secure-password
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
JWT_SECRET_KEY=xxx (min 32 chars)

# Stripe (required for payments/subscriptions)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_STARTER_MONTHLY=price_xxx
STRIPE_PRICE_ID_STARTER_YEARLY=price_xxx
STRIPE_PRICE_ID_PRO_MONTHLY=price_xxx
STRIPE_PRICE_ID_PRO_YEARLY=price_xxx
STRIPE_PRICE_ID_UNLIMITED_MONTHLY=price_xxx
STRIPE_PRICE_ID_UNLIMITED_YEARLY=price_xxx

# URLs (set per environment)
DOMAIN=launchpad.example.com
FRONTEND_URL=https://launchpad.example.com
GOOGLE_REDIRECT_URI=https://launchpad.example.com/api/v1/auth/google/callback
```

**Important**: All environment variables in `.env` must also be mapped in `docker-compose.*.yml` files under the `backend.environment` section.

## Architecture

- **Frontend**: Vue 3 + Vite + TypeScript + TailwindCSS + shadcn-vue
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Auth**: Google OAuth with JWT
- **Payments**: Stripe
- **Reverse Proxy**: Traefik (auto SSL)

## Frontend Guidelines

- **Always use shadcn-vue components** when possible (Button, Badge, Input, etc.)
- Install new components: `pnpm dlx shadcn-vue@latest add <component>`
- Components are in `src/components/ui/`
- **NEVER modify files in `src/components/ui/`** - these are shadcn-vue components
- Prefer shadcn styling over custom CSS

## Key Files

- `docker-compose.yml` - Local development
- `docker-compose.dev.yml` - Dev VPS config
- `docker-compose.prod.yml` - Production config
- `backend/` - FastAPI app
- `src/` - Vue frontend source
- `cli/` - CLI tool for project management
