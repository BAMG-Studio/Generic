#!/bin/bash

##############################################################################
# Setup SSH Key Authentication for ForgeTrace VPS
##############################################################################

set -e

VPS_IP="${VPS_IP:-148.230.94.85}"
VPS_USER="${VPS_USER:-root}"

echo "🔐 Setting up SSH key authentication for ${VPS_USER}@${VPS_IP}"
echo ""

# Check if SSH key exists
if [ ! -f ~/.ssh/id_ed25519 ] && [ ! -f ~/.ssh/id_rsa ]; then
    echo "📝 No SSH key found. Generating new ED25519 key..."
    ssh-keygen -t ed25519 -C "forgetrace-deploy-$(date +%Y%m%d)" -f ~/.ssh/id_ed25519 -N ""
    echo "✅ SSH key generated: ~/.ssh/id_ed25519"
else
    echo "✅ SSH key already exists"
fi

# Copy public key to VPS
echo ""
echo "📤 Copying SSH public key to VPS..."
echo "   You will be prompted for the VPS root password"
echo ""

if [ -f ~/.ssh/id_ed25519.pub ]; then
    KEY_FILE=~/.ssh/id_ed25519.pub
elif [ -f ~/.ssh/id_rsa.pub ]; then
    KEY_FILE=~/.ssh/id_rsa.pub
else
    echo "❌ No public key found"
    exit 1
fi

# Try ssh-copy-id first
if command -v ssh-copy-id &> /dev/null; then
    ssh-copy-id -i ${KEY_FILE} ${VPS_USER}@${VPS_IP}
else
    # Manual method
    echo "⚠️  ssh-copy-id not found. Using manual method..."
    cat ${KEY_FILE} | ssh ${VPS_USER}@${VPS_IP} "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
fi

# Test connection
echo ""
echo "🧪 Testing SSH connection without password..."
if ssh -o BatchMode=yes ${VPS_USER}@${VPS_IP} exit 2>/dev/null; then
    echo "✅ SSH key authentication successful!"
    echo ""
    echo "🎉 You can now deploy without passwords:"
    echo "   ./scripts/deploy_to_vps.sh"
else
    echo "❌ SSH key authentication failed. Check VPS configuration."
    exit 1
fi
