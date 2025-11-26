#!/bin/bash
set -e

echo "🚀 ForgeTrace Simple Deployment to VPS"
echo "======================================="
echo ""
echo "This will deploy ForgeTrace to forgetrace.pro (148.230.94.85)"
echo ""
echo "⚠️  You will be prompted for the VPS password multiple times"
echo ""

VPS="root@148.230.94.85"
DEPLOY_PATH="/opt/forgetrace"

# Build frontend
echo "🏗️  Building frontend..."
cd forge_platform/frontend
npm install
npm run build
cd ../..

# Sync files
echo ""
echo "📦 Syncing files to VPS..."
rsync -avz --delete \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='mlruns/' \
  ./ ${VPS}:${DEPLOY_PATH}/

echo ""
echo "✅ Files synced successfully!"
echo ""
echo "🔧 Next: SSH to VPS and run setup commands"
echo "   ssh ${VPS}"
echo "   cd ${DEPLOY_PATH}"
echo "   source .venv/bin/activate"
echo "   pip install -r requirements.txt"

