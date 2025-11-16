#!/usr/bin/env bash
# ForgeTrace Complete Production Setup
# One command to deploy everything

set -euo pipefail

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║  ForgeTrace Production Deployment - Complete Setup                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Deploy AWS Infrastructure
echo "Step 1/4: Deploying AWS Infrastructure..."
echo "  → IAM user, S3 bucket, CloudTrail, CloudWatch"
cd terraform/
./deploy.sh full

if [ $? -ne 0 ]; then
    echo "❌ AWS deployment failed. Please check errors above."
    exit 1
fi

echo ""
echo "✅ AWS Infrastructure deployed!"
echo ""

# Step 2: Save credentials
echo "Step 2/4: Saving AWS Credentials..."
mkdir -p ~/.forgetrace
terraform output -json > ~/.forgetrace/aws-outputs.json
echo "  → Saved to: ~/.forgetrace/aws-outputs.json"
echo ""

# Step 3: Display GitHub setup instructions
echo "Step 3/4: GitHub Token & Secrets Setup"
echo "  ⚠️  MANUAL ACTION REQUIRED:"
echo ""
echo "  1. Generate GitHub Token (5 min):"
echo "     → https://github.com/settings/tokens"
echo "     → Scopes: repo, workflow, write:packages"
echo ""
echo "  2. Add GitHub Secrets (10 min):"
echo "     → https://github.com/BAMG-Studio/Generic/settings/secrets/actions"
echo ""

# Display secrets reference
terraform output github_secrets_reference

echo ""
read -p "Press ENTER after adding GitHub Secrets..."

# Step 4: Deploy MLflow
echo ""
echo "Step 4/4: Deploying MLflow..."
cd ..

# Create .env file
cat > .env << EOF
AWS_ACCESS_KEY_ID=$(cd terraform && terraform output -raw aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(cd terraform && terraform output -raw aws_secret_access_key)
AWS_DEFAULT_REGION=us-east-1
DVC_REMOTE_BUCKET=$(cd terraform && terraform output -raw s3_bucket_name)
MLFLOW_DB_PASSWORD=change_this_password_123
EOF

echo "  → Created .env file"

# Start MLflow
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ MLflow deployed!"
    echo "  → Access: http://localhost:5000"
else
    echo "⚠️  MLflow deployment failed (Docker not running?)"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║  DEPLOYMENT COMPLETE!                                                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ AWS Infrastructure: Deployed"
echo "✅ Credentials: Saved to ~/.forgetrace/aws-outputs.json"
echo "✅ MLflow: Running at http://localhost:5000"
echo ""
echo "Next Steps:"
echo "  1. Run test audit: forgetrace audit test_output/ml_demo_repo/"
echo "  2. Create test PR to verify CI/CD pipeline"
echo "  3. Review SECURITY.md for credential rotation schedule"
echo ""
echo "Total deployment time: ~30 minutes"
echo "Monthly AWS cost: ~\$5-10"
echo ""
