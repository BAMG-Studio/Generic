#!/bin/bash
# OAuth Setup Guide for ForgeTrace Platform
# Interactive script to configure GitHub and Google OAuth

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}ForgeTrace OAuth Setup${NC}"
echo "================================"
echo ""

# Backend .env file path
ENV_FILE="forge_platform/backend/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: $ENV_FILE not found${NC}"
    exit 1
fi

echo -e "${BLUE}This script will help you configure OAuth providers.${NC}"
echo ""

# GitHub OAuth Setup
echo -e "${GREEN}1. GitHub OAuth Setup${NC}"
echo "================================"
echo ""
echo "Steps to create GitHub OAuth App:"
echo "1. Go to: https://github.com/settings/developers"
echo "2. Click 'New OAuth App'"
echo "3. Configure:"
echo "   - Application name: ForgeTrace Platform"
echo "   - Homepage URL: http://localhost:3001 (or your production URL)"
echo "   - Authorization callback URL: http://localhost:8001/api/v1/auth/callback/github"
echo "4. Click 'Register application'"
echo "5. Copy the Client ID and generate a Client Secret"
echo ""

read -p "Do you want to configure GitHub OAuth? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter GitHub Client ID: " GITHUB_CLIENT_ID
    read -sp "Enter GitHub Client Secret: " GITHUB_CLIENT_SECRET
    echo
    
    # Update .env file
    sed -i "s|GITHUB_CLIENT_ID=.*|GITHUB_CLIENT_ID=$GITHUB_CLIENT_ID|" "$ENV_FILE"
    sed -i "s|GITHUB_CLIENT_SECRET=.*|GITHUB_CLIENT_SECRET=$GITHUB_CLIENT_SECRET|" "$ENV_FILE"
    
    echo -e "${GREEN}✓ GitHub OAuth configured${NC}"
else
    echo "Skipping GitHub OAuth setup"
fi

echo ""
echo ""

# Google OAuth Setup
echo -e "${GREEN}2. Google OAuth Setup${NC}"
echo "================================"
echo ""
echo "Steps to create Google OAuth App:"
echo "1. Go to: https://console.cloud.google.com/apis/credentials"
echo "2. Create a new project or select existing"
echo "3. Click 'Create Credentials' > 'OAuth client ID'"
echo "4. Configure consent screen if prompted"
echo "5. Choose 'Web application'"
echo "6. Configure:"
echo "   - Name: ForgeTrace Platform"
echo "   - Authorized redirect URIs:"
echo "     * http://localhost:8001/api/v1/auth/callback/google"
echo "     * (add production URL when deploying)"
echo "7. Copy the Client ID and Client Secret"
echo ""

read -p "Do you want to configure Google OAuth? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter Google Client ID: " GOOGLE_CLIENT_ID
    read -sp "Enter Google Client Secret: " GOOGLE_CLIENT_SECRET
    echo
    
    # Update .env file
    sed -i "s|GOOGLE_CLIENT_ID=.*|GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID|" "$ENV_FILE"
    sed -i "s|GOOGLE_CLIENT_SECRET=.*|GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET|" "$ENV_FILE"
    
    echo -e "${GREEN}✓ Google OAuth configured${NC}"
else
    echo "Skipping Google OAuth setup"
fi

echo ""
echo ""
echo -e "${GREEN}✓ OAuth setup complete!${NC}"
echo ""
echo "Configuration saved to: $ENV_FILE"
echo ""
echo "Next steps:"
echo "1. Restart the backend server to apply changes"
echo "2. Test OAuth login at: http://localhost:3001/login"
echo "3. OAuth endpoints:"
echo "   - GitHub: GET /api/v1/auth/oauth/github"
echo "   - Google: GET /api/v1/auth/oauth/google"
echo ""
echo "For production deployment:"
echo "- Update callback URLs to use your production domain"
echo "- Add production URLs to OAuth app configurations"
echo "- Update OAUTH_CALLBACK_URL in backend/.env"
echo ""
