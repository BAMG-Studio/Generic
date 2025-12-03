#!/bin/bash
set -e

echo "=== ForgeTrace Token System Deployment ==="
echo ""

# Configuration
VPS_HOST="root@148.230.94.85"
FRONTEND_DIST="/home/papaert/projects/ForgeTrace/forge_platform/frontend/dist"
BACKEND_DIR="/home/papaert/projects/ForgeTrace/forge_platform/backend"
REMOTE_FRONTEND="/opt/forgetrace/forge_platform/frontend/dist"
REMOTE_BACKEND="/opt/forgetrace/forge_platform/backend"

echo "Step 1: Syncing frontend build to VPS..."
rsync -avz --delete "${FRONTEND_DIST}/" "${VPS_HOST}:${REMOTE_FRONTEND}/"
echo "✓ Frontend synced"
echo ""

echo "Step 2: Syncing backend code to VPS..."
rsync -avz --exclude '__pycache__' --exclude '*.pyc' --exclude '.venv' \
  "${BACKEND_DIR}/" "${VPS_HOST}:${REMOTE_BACKEND}/"
echo "✓ Backend synced"
echo ""

echo "Step 3: Running database migrations on VPS..."
ssh "${VPS_HOST}" << 'ENDSSH'
  cd /opt/forgetrace/forge_platform/backend
  source /opt/forgetrace/.venv/bin/activate
  python -m alembic upgrade head
  echo "✓ Migrations applied"
ENDSSH
echo ""

echo "Step 4: Restarting backend service..."
ssh "${VPS_HOST}" "systemctl restart forgetrace-backend"
echo "✓ Backend restarted"
echo ""

echo "Step 5: Checking service status..."
ssh "${VPS_HOST}" "systemctl status forgetrace-backend --no-pager" || true
echo ""

echo "=== Deployment Complete ==="
echo ""
echo "Frontend: https://www.forgetrace.pro/app/"
echo "Developer Portal: https://www.forgetrace.pro/app/developer"
echo "API: https://api.forgetrace.pro/api/v1/"
echo ""
echo "Next steps:"
echo "1. Test the Developer portal: https://www.forgetrace.pro/app/developer"
echo "2. Create a test token"
echo "3. Verify token endpoints work"
echo "4. Test rate limiting"
