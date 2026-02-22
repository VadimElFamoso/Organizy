#!/bin/bash

# Quick redeploy script for Launchpad
# Usage: ./redeploy.sh [prod|dev|both]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }

TARGET=${1:-both}

redeploy_prod() {
    print_status "Redeploying production..."
    cd /opt/launchpad

    git pull origin main || git pull origin master

    print_status "Building images (containers still running)..."
    docker compose -f docker-compose.prod.yml build

    print_status "Swapping containers..."
    docker compose -f docker-compose.prod.yml up -d

    print_status "Waiting for backend to be ready..."
    sleep 5

    print_status "Running database migrations..."
    docker compose -f docker-compose.prod.yml exec -T backend uv run alembic upgrade head

    print_status "Production redeployed!"
    docker compose -f docker-compose.prod.yml ps
}

redeploy_dev() {
    print_status "Redeploying dev..."
    cd /opt/launchpad-dev

    git pull origin main || git pull origin master

    print_status "Building images (containers still running)..."
    docker compose -f docker-compose.dev.yml build

    print_status "Swapping containers..."
    docker compose -f docker-compose.dev.yml up -d

    print_status "Waiting for backend to be ready..."
    sleep 5

    print_status "Running database migrations..."
    docker compose -f docker-compose.dev.yml exec -T backend uv run alembic upgrade head

    print_status "Dev redeployed!"
    docker compose -f docker-compose.dev.yml ps
}

case $TARGET in
    prod)
        redeploy_prod
        ;;
    dev)
        redeploy_dev
        ;;
    both)
        redeploy_prod
        echo ""
        redeploy_dev
        ;;
    *)
        echo "Usage: $0 [prod|dev|both]"
        exit 1
        ;;
esac

echo ""
print_status "Done!"
