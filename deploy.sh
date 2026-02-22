#!/bin/bash

# Launchpad Deployment Script for VPS
# Deploys both prod and dev environments

set -e

echo "Starting Launchpad deployment..."

# Configuration
REPO_URL="https://github.com/lorisalx/launchpad.git"  # Update this!
PROD_DIR="/opt/launchpad"
DEV_DIR="/opt/launchpad-dev"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[OK]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

# Install dependencies if needed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    apt-get update
    apt-get install -y docker.io docker-compose-plugin git
    systemctl enable docker
    systemctl start docker
fi

# Setup firewall
print_status "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Clone or update PRODUCTION
if [ -d "$PROD_DIR" ]; then
    print_status "Updating production repository..."
    cd $PROD_DIR
    git pull origin main || git pull origin master
else
    print_status "Cloning production repository..."
    git clone $REPO_URL $PROD_DIR
fi

# Clone or update DEV
if [ -d "$DEV_DIR" ]; then
    print_status "Updating dev repository..."
    cd $DEV_DIR
    git pull origin main || git pull origin master
else
    print_status "Cloning dev repository..."
    git clone $REPO_URL $DEV_DIR
fi

# Create .env files if they don't exist
for DIR in $PROD_DIR $DEV_DIR; do
    if [ ! -f "$DIR/.env" ]; then
        print_warning "Creating .env template in $DIR..."
        cat > "$DIR/.env" << 'EOF'
# Environment
ENVIRONMENT=dev

# Database
POSTGRES_PASSWORD=change-me-secure-password

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-me

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_PRO_MONTHLY=price_xxx
STRIPE_PRICE_ID_PRO_YEARLY=price_xxx

# URLs
DOMAIN=your-domain.com
FRONTEND_URL=https://your-domain.com
GOOGLE_REDIRECT_URI=https://your-domain.com/api/v1/auth/google/callback
EOF
    fi
done

# Deploy PRODUCTION
print_status "Deploying production..."
cd $PROD_DIR
docker compose -f docker-compose.prod.yml down --remove-orphans || true
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Deploy DEV
print_status "Deploying dev environment..."
cd $DEV_DIR
docker compose -f docker-compose.dev.yml down --remove-orphans || true
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml up -d

# Wait for services
print_status "Waiting for services to start..."
sleep 15

# Create systemd services
print_status "Creating systemd services..."

cat > /etc/systemd/system/launchpad.service << EOF
[Unit]
Description=Launchpad Production
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROD_DIR
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/launchpad-dev.service << EOF
[Unit]
Description=Launchpad Dev
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEV_DIR
ExecStart=/usr/bin/docker compose -f docker-compose.dev.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.dev.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable launchpad
systemctl enable launchpad-dev

# Show status
print_status "Deployment complete!"
echo ""
echo "Production containers:"
cd $PROD_DIR && docker compose -f docker-compose.prod.yml ps
echo ""
echo "Dev containers:"
cd $DEV_DIR && docker compose -f docker-compose.dev.yml ps
echo ""

print_warning "Next steps:"
echo "  1. Configure .env files in $PROD_DIR and $DEV_DIR"
echo "  2. Run: cd $PROD_DIR && docker compose -f docker-compose.prod.yml restart"
echo "  3. Run: cd $DEV_DIR && docker compose -f docker-compose.dev.yml restart"
