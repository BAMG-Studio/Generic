# ForgeTrace Production Deployment Guide

Complete step-by-step guide to deploy ForgeTrace to production with AWS, MLflow, and GitHub Actions.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Setup](#aws-setup)
3. [GitHub Configuration](#github-configuration)
4. [MLflow Deployment](#mlflow-deployment)
5. [GitHub Secrets Configuration](#github-secrets-configuration)
6. [CI/CD Pipeline Setup](#cicd-pipeline-setup)
7. [Branch Protection](#branch-protection)
8. [Deployment Validation](#deployment-validation)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- [x] AWS Account
- [x] GitHub Account with admin access to repository
- [x] Docker & Docker Compose (for MLflow)
- [x] AWS CLI v2
- [x] Python 3.10+
- [x] Git

### Cost Estimate

| Service | Monthly Cost | Notes |
|---------|--------------|-------|
| AWS S3 | $1-3 | Model storage (<10 GB) |
| AWS CloudWatch | $2-5 | Logs retention (90 days) |
| MLflow (self-hosted) | $0 | Docker on your server |
| GitHub Actions | $0 | Public repos, 2000 min/month free |
| **Total** | **$5-10** | Minimal production setup |

---

## AWS Setup

### Step 1: Create IAM User

```bash
# 1. Log in to AWS Console: https://console.aws.amazon.com

# 2. Navigate to IAM
#    Search bar → "IAM" → Click "IAM"

# 3. Create user
#    Left sidebar → "Users" → "Create user"
#    - User name: forgetrace-ci
#    - ✅ Provide user access to AWS Management Console (optional)
#    - Click "Next"

# 4. Set permissions
#    - Select "Attach policies directly"
#    - Search and check:
#      ✅ AmazonS3FullAccess
#      ✅ CloudWatchLogsFullAccess
#    - Click "Next" → "Create user"

# 5. Create access key
#    - Click on "forgetrace-ci" user
#    - "Security credentials" tab
#    - Scroll to "Access keys" → "Create access key"
#    - Select "Application running outside AWS"
#    - Click "Next" → Add description: "ForgeTrace CI/CD Pipeline"
#    - Click "Create access key"

# 6. ⚠️ SAVE CREDENTIALS IMMEDIATELY
#    AWS_ACCESS_KEY_ID: AKIA................
#    AWS_SECRET_ACCESS_KEY: ........................................
#    (40 characters)

# 7. Download .csv file as backup
```

### Step 2: Create S3 Bucket

```bash
# 1. Navigate to S3
#    AWS Console → Search "S3" → Click "S3"

# 2. Create bucket
#    - Click "Create bucket"
#    - Bucket name: forgetrace-models-<your-initials>-<random-digits>
#      Example: forgetrace-models-pk-8472
#    - AWS Region: us-east-1 (or closest to you)
#    - Block Public Access: ✅ KEEP ALL CHECKED (private bucket)
#    - Bucket Versioning: Enable
#    - Default encryption: Enable (SSE-S3)
#    - Click "Create bucket"

# 3. Create folder structure
#    Click on bucket → "Create folder" → Name: models/
#    Repeat for:
#    - training-data/
#    - benchmarks/
#    - audit-reports/
#    - mlflow/

# 4. (Optional) Configure lifecycle policy to save costs
#    Bucket → "Management" tab → "Create lifecycle rule"
#    - Rule name: archive-old-models
#    - Apply to: models/
#    - ✅ Transition to Glacier after 90 days
#    - ✅ Delete after 365 days
#    - Click "Create rule"
```

### Step 3: Test AWS Configuration

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter:
#   AWS Access Key ID: AKIA...
#   AWS Secret Access Key: ...
#   Default region name: us-east-1
#   Default output format: json

# Test connection
aws s3 ls s3://forgetrace-models-pk-8472/

# Expected output: Empty list or your folders
# PRE audit-reports/
# PRE benchmarks/
# PRE mlflow/
# PRE models/
# PRE training-data/

# Test write access
echo "test" > test.txt
aws s3 cp test.txt s3://forgetrace-models-pk-8472/ci-test/test.txt
aws s3 rm s3://forgetrace-models-pk-8472/ci-test/test.txt
rm test.txt

echo "✅ AWS S3 connection successful"
```

---

## GitHub Configuration

### Step 1: Generate Personal Access Token

```bash
# 1. Navigate to GitHub Settings
#    GitHub.com → Profile (top right) → Settings

# 2. Go to Developer Settings
#    Left sidebar (bottom) → Developer settings
#    → Personal access tokens → Tokens (classic)

# 3. Generate new token
#    "Generate new token" → "Generate new token (classic)"

# 4. Configure token
#    Note: ForgeTrace CI/CD Pipeline
#    Expiration: 90 days (recommended) or No expiration
#    
#    Select scopes:
#    ✅ repo (all sub-options)
#    ✅ workflow
#    ✅ write:packages
#    ✅ read:org (if using organization)

# 5. Generate and save
#    Scroll down → "Generate token"
#    
#    ⚠️ COPY TOKEN IMMEDIATELY (shown only once)
#    ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 6. Store securely
#    - Password manager (1Password, LastPass)
#    - Environment variable (see below)
```

### Step 2: Store Token Locally

```bash
# Option A: Environment variable
echo 'export GITHUB_TOKEN="ghp_xxxxx..."' >> ~/.bashrc
source ~/.bashrc

# Option B: .env file (never commit to Git)
cat > .env << 'EOF'
GITHUB_TOKEN=ghp_xxxxx...
EOF

# Ensure .env is in .gitignore
echo ".env" >> .gitignore
```

### Step 3: Test GitHub Token

```bash
# Test API access
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/user

# Expected output: Your GitHub user info (JSON)
```

---

## MLflow Deployment

### Option A: Self-Hosted (Recommended)

#### Step 1: Create Environment File

```bash
# Create .env file for MLflow
cat > .env << EOF
# AWS credentials for S3 artifact storage
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1

# S3 bucket for MLflow artifacts
DVC_REMOTE_BUCKET=forgetrace-models-pk-8472

# MLflow database password
MLFLOW_DB_PASSWORD=change_this_password_123

# S3 endpoint
MLFLOW_S3_ENDPOINT_URL=https://s3.amazonaws.com
EOF
```

#### Step 2: Deploy with Docker Compose

```bash
# Start MLflow services
docker-compose up -d

# Check status
docker-compose ps

# Expected output:
# NAME                    IMAGE                           STATUS
# forgetrace-mlflow       ghcr.io/mlflow/mlflow:v2.9.0   Up
# forgetrace-postgres     postgres:15-alpine              Up

# View logs
docker-compose logs -f mlflow

# Access UI
open http://localhost:5000
```

#### Step 3: (Optional) Enable Authentication

```bash
# Install htpasswd
sudo apt install apache2-utils  # Debian/Ubuntu
# OR
brew install httpd  # macOS

# Create password file
cd deployment/nginx
htpasswd -c .htpasswd mlflow_admin
# Enter password when prompted

# Start with authentication
docker-compose --profile with-auth up -d

# Test authenticated access
curl -u mlflow_admin:your_password http://localhost/api/2.0/mlflow/experiments/list
```

### Option B: AWS SageMaker (Managed)

```bash
# 1. Navigate to AWS SageMaker
#    AWS Console → Search "SageMaker" → Click "SageMaker"

# 2. Create MLflow Tracking Server
#    Left sidebar → "Tracking Servers" → "Create tracking server"
#    - Tracking server name: forgetrace-mlflow
#    - Artifact store: s3://forgetrace-models-pk-8472/mlflow/
#    - Database: Create new RDS instance (or use existing)
#    - Click "Create"

# 3. Get tracking URI
#    After creation, copy the "Tracking server ARN"
#    Example: arn:aws:sagemaker:us-east-1:123456789:mlflow-tracking-server/forgetrace-mlflow

# Cost: ~$50-100/month for managed service
```

---

## GitHub Secrets Configuration

### Step 1: Add Secrets to Repository

```bash
# 1. Navigate to repository settings
#    Your ForgeTrace repo → Settings

# 2. Go to Secrets and variables
#    Left sidebar → Secrets and variables → Actions

# 3. Add each secret
#    Click "New repository secret"

# Add these secrets one by one:
```

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `AWS_ACCESS_KEY_ID` | `AKIA...` | From IAM user creation |
| `AWS_SECRET_ACCESS_KEY` | `wJalr...` | From IAM user creation (40 chars) |
| `AWS_DEFAULT_REGION` | `us-east-1` | Your AWS region |
| `DVC_REMOTE_BUCKET` | `forgetrace-models-pk-8472` | Your S3 bucket name |
| `GITHUB_TOKEN` | `ghp_...` | Personal access token |
| `MLFLOW_TRACKING_URI` | `http://your-server:5000` | Self-hosted or SageMaker ARN |
| `MLFLOW_USERNAME` | `mlflow_admin` | Optional, if using auth |
| `MLFLOW_PASSWORD` | `your_password` | Optional, if using auth |

### Step 2: Verify Secrets

```bash
# Trigger the test workflow
# Go to: Actions tab → "Test Secrets Configuration" → "Run workflow"

# Check output for:
# ✅ AWS credentials format valid
# ✅ S3 connection successful
# ✅ GitHub token valid
# ✅ MLflow connection successful
```

---

## CI/CD Pipeline Setup

### Step 1: Verify Workflows

```bash
# Check that workflow files exist
ls -la .github/workflows/

# Expected:
# ci.yml              # Main CI/CD pipeline
# ml-training.yml     # ML model training
# test-secrets.yml    # Secret validation
```

### Step 2: Enable GitHub Actions

```bash
# 1. Repository → Settings → Actions → General

# 2. Allow actions:
#    ✅ Allow all actions and reusable workflows

# 3. Workflow permissions:
#    ✅ Read and write permissions
#    ✅ Allow GitHub Actions to create and approve pull requests

# 4. Click "Save"
```

### Step 3: Trigger First Pipeline

```bash
# Option A: Push to main branch
git add .
git commit -m "feat: configure production infrastructure"
git push origin main

# Option B: Manual trigger
# Go to: Actions → "CI/CD Pipeline" → "Run workflow"

# Monitor progress in Actions tab
```

---

## Branch Protection

### Step 1: Configure Protection Rules

```bash
# 1. Repository → Settings → Branches

# 2. Add branch protection rule
#    Click "Add branch protection rule"

# 3. Branch name pattern: main

# 4. Configure rules:
```

**Required Settings**:
- [x] Require a pull request before merging
  - [x] Require approvals: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners
- [x] Require status checks to pass before merging
  - [x] Require branches to be up to date before merging
  - Search and add:
    - `CI/CD Pipeline / lint`
    - `CI/CD Pipeline / test`
    - `CI/CD Pipeline / security`
- [x] Require conversation resolution before merging
- [x] Do not allow bypassing the above settings

### Step 2: Verify CODEOWNERS

```bash
# Ensure CODEOWNERS file exists
cat .github/CODEOWNERS

# Expected output:
# * @papaert-cloud
# /training/ @papaert-cloud
# ...
```

---

## Deployment Validation

### Checklist

Run through this checklist to verify deployment:

```bash
# ✅ AWS Configuration
aws s3 ls s3://forgetrace-models-pk-8472/
aws cloudtrail describe-trails  # (if enabled)

# ✅ MLflow
curl http://localhost:5000/health
# OR
curl $MLFLOW_TRACKING_URI/health

# ✅ GitHub Actions
# Actions tab → "Test Secrets Configuration" → Run workflow
# Verify all checks pass

# ✅ Branch Protection
# Try to push directly to main (should fail)
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "test: verify branch protection"
git push origin main
# Expected: remote: error: GH006: Protected branch update failed

# ✅ PR Workflow
git checkout -b test-branch
git push origin test-branch
# Create PR on GitHub → Verify status checks run

# ✅ ML Training Pipeline
# Actions → "ML Training Pipeline" → Run workflow
# Verify model trains and uploads to S3
```

---

## Monitoring & Maintenance

### Daily Checks

```bash
# Check GitHub Actions status
# Actions tab → View recent workflow runs

# Check for Dependabot alerts
# Security tab → Dependabot alerts

# Review MLflow experiments
open http://localhost:5000  # or your MLflow URI
```

### Weekly Tasks

```bash
# Review audit logs
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=forgetrace-ci \
  --max-results 50

# Check S3 storage usage
aws s3 ls s3://forgetrace-models-pk-8472/ --recursive --summarize

# Review security scan results
# Actions → Latest "CI/CD Pipeline" → "security" job
```

### Monthly Tasks

```bash
# Review and update dependencies
pip list --outdated
pip-audit

# Review GitHub Secret expiration
# Settings → Secrets and variables → Check token expiration dates

# Backup critical data
aws s3 sync s3://forgetrace-models-pk-8472/models/ ./backups/models/

# Review SECURITY.md for secret rotation schedule
```

### Quarterly Tasks

```bash
# Rotate secrets (see SECURITY.md)
# Update AWS access keys
# Update GitHub tokens
# Update MLflow passwords

# Review and update branch protection rules
# Audit access permissions
# Update documentation
```

---

## Troubleshooting

### AWS Issues

**Problem**: `AccessDenied` error when accessing S3

```bash
# Solution: Verify IAM permissions
aws iam list-user-policies --user-name forgetrace-ci
aws iam list-attached-user-policies --user-name forgetrace-ci

# Ensure AmazonS3FullAccess is attached
```

**Problem**: `NoSuchBucket` error

```bash
# Solution: Verify bucket name and region
aws s3api head-bucket --bucket forgetrace-models-pk-8472
# Check that region matches AWS_DEFAULT_REGION
```

### GitHub Actions Issues

**Problem**: `Secret not found` error

```bash
# Solution: Verify secret exists
# Settings → Secrets and variables → Actions
# Ensure secret name matches exactly (case-sensitive)
```

**Problem**: Workflow not triggering

```bash
# Solution: Check workflow syntax
# Use GitHub Actions validator: https://rhysd.github.io/actionlint/

# Or install locally:
brew install actionlint
actionlint .github/workflows/*.yml
```

### MLflow Issues

**Problem**: Cannot connect to MLflow server

```bash
# Solution 1: Check container status
docker-compose ps
docker-compose logs mlflow

# Solution 2: Verify port is accessible
curl http://localhost:5000/health

# Solution 3: Check firewall rules
sudo ufw status  # Linux
# Ensure port 5000 is open
```

**Problem**: MLflow cannot write to S3

```bash
# Solution: Test AWS credentials in container
docker-compose exec mlflow bash
aws s3 ls s3://forgetrace-models-pk-8472/

# If fails, check .env file has correct AWS credentials
```

### DVC Issues

**Problem**: `ERROR: failed to pull data from the cloud`

```bash
# Solution: Verify DVC remote configuration
dvc remote list
dvc remote modify s3remote region us-east-1

# Test S3 access
dvc pull --verbose
```

---

## Next Steps

After successful deployment:

1. **Train Initial Model**
   ```bash
   # Trigger training pipeline
   # Actions → "ML Training Pipeline" → Run workflow
   ```

2. **Run First Audit**
   ```bash
   forgetrace audit /path/to/repo --out ./results
   ```

3. **Set Up Client Profiling**
   ```bash
   # See: training/profiling_datasets/README.md
   python scripts/extract_profile_samples.py \
     --input /path/to/client/repo \
     --output training/profiling_datasets/client_profile_1/
   ```

4. **Review Security Policy**
   ```bash
   # See: SECURITY.md
   # Set up secret rotation reminders
   # Enable CloudTrail for audit logging
   ```

---

## Support

For deployment assistance:
- **Email**: peter@beaconagile.net
- **Documentation**: See `README.md`, `USAGE.md`, `ARCHITECTURE.md`
- **Issues**: Open GitHub issue with `deployment` label

---

**Last Updated**: 2025-11-16  
**Next Review**: 2026-02-16
