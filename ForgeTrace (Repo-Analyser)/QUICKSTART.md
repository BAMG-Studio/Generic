# ForgeTrace Production Quick Start Guide

**Get ForgeTrace production-ready in 30 minutes.**

This is a condensed version of the full deployment guide. For detailed instructions, see `docs/PRODUCTION_DEPLOYMENT.md`.

---

## 🚀 Quick Setup (30 Minutes)

### Prerequisites
- AWS Account
- GitHub Account (admin access to repo)
- Docker & Docker Compose
- Python 3.10+

---

## Step 1: AWS Setup (10 minutes)

```bash
# 1. Create IAM user "forgetrace-ci" in AWS Console
#    Attach policies: AmazonS3FullAccess, CloudWatchLogsFullAccess

# 2. Create access key, save credentials:
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# 3. Create S3 bucket
#    Name: forgetrace-models-<your-suffix>
#    Region: us-east-1
#    Create folders: models/, training-data/, mlflow/

# 4. Test connection
pip install awscli
aws configure  # Enter credentials
aws s3 ls s3://forgetrace-models-<your-suffix>/
```

---

## Step 2: GitHub Token (5 minutes)

```bash
# 1. Generate token: GitHub.com → Settings → Developer Settings → Personal Access Tokens
#    Scopes: repo, workflow, write:packages

# 2. Save token
GITHUB_TOKEN=ghp_xxxxx...

# 3. Test
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

---

## Step 3: MLflow Deployment (10 minutes)

```bash
# 1. Create .env file
cat > .env << EOF
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
DVC_REMOTE_BUCKET=forgetrace-models-<your-suffix>
MLFLOW_DB_PASSWORD=change_this_password_123
MLFLOW_S3_ENDPOINT_URL=https://s3.amazonaws.com
EOF

# 2. Start MLflow
docker-compose up -d

# 3. Verify
docker-compose ps
open http://localhost:5000  # MLflow UI should load
```

---

## Step 4: Configure GitHub Secrets (5 minutes)

Go to: **Repository → Settings → Secrets and Variables → Actions**

Add these secrets:

| Name | Value |
|------|-------|
| `AWS_ACCESS_KEY_ID` | From Step 1 |
| `AWS_SECRET_ACCESS_KEY` | From Step 1 |
| `AWS_DEFAULT_REGION` | `us-east-1` |
| `DVC_REMOTE_BUCKET` | `forgetrace-models-<suffix>` |
| `GITHUB_TOKEN` | From Step 2 |
| `MLFLOW_TRACKING_URI` | `http://your-server:5000` |

---

## Step 5: Enable CI/CD & Branch Protection (5 minutes)

```bash
# 1. Enable GitHub Actions
#    Repository → Settings → Actions → General
#    ✅ Allow all actions
#    ✅ Read and write permissions

# 2. Configure branch protection
#    Settings → Branches → Add rule for "main"
#    ✅ Require pull request before merging (1 approval)
#    ✅ Require status checks (lint, test, security)
#    ✅ Require conversation resolution

# 3. Verify workflows
#    Actions → "Test Secrets Configuration" → Run workflow
#    Should pass all checks ✅
```

---

## ✅ Verification

Test the complete setup:

```bash
# 1. Local audit test
forgetrace audit test_output/ml_demo_repo/ --out validation/

# 2. Create test PR
git checkout -b test-deployment
echo "# Test" >> README.md
git add README.md
git commit -m "test: verify CI/CD"
git push origin test-deployment

# 3. Open PR on GitHub
#    - CI/CD should run automatically
#    - Status checks should pass
#    - Cannot merge without approval

# 4. Trigger ML training
#    Actions → "ML Training Pipeline" → Run workflow
#    Should train model and upload to S3
```

---

## 📋 Post-Deployment

### Immediate Tasks
- [ ] Review `SECURITY.md` and set secret rotation reminders
- [ ] Review `docs/EDGE_CASES.md` for client profiling guidance
- [ ] Update `.env` with production values
- [ ] Schedule first maintenance window

### Weekly Maintenance
- [ ] Check GitHub Actions status
- [ ] Review Dependabot alerts
- [ ] Check S3 storage usage

### Monthly Maintenance
- [ ] Update dependencies (`pip list --outdated`)
- [ ] Run security audit (`pip-audit`)
- [ ] Review access logs

---

## 🔧 Troubleshooting

### AWS Connection Failed
```bash
# Verify credentials
aws sts get-caller-identity

# Check bucket exists
aws s3 ls s3://forgetrace-models-<suffix>/
```

### MLflow Not Starting
```bash
# Check container logs
docker-compose logs mlflow

# Restart services
docker-compose down
docker-compose up -d
```

### GitHub Actions Failing
```bash
# Test secrets locally
source .env
python -c "import os; print(os.environ.get('AWS_ACCESS_KEY_ID'))"

# Check workflow syntax
actionlint .github/workflows/*.yml
```

---

## 📚 Full Documentation

- **Complete Deployment Guide**: `docs/PRODUCTION_DEPLOYMENT.md`
- **Deployment Checklist**: `docs/DEPLOYMENT_CHECKLIST.md`
- **Security Policy**: `SECURITY.md`
- **Edge Cases**: `docs/EDGE_CASES.md`
- **Architecture**: `ARCHITECTURE.md`
- **Usage Guide**: `USAGE.md`

---

## 🆘 Support

- **Email**: peter@beaconagile.net
- **GitHub Issues**: Open issue with `deployment` label
- **Security Issues**: Email directly (never public issue)

---

## 🎯 Next Steps

After successful deployment:

1. **Train Initial Model**
   ```bash
   # Trigger via GitHub Actions
   Actions → "ML Training Pipeline" → Run workflow
   ```

2. **Run First Audit**
   ```bash
   forgetrace audit /path/to/client/repo \
     --out repo_audit/<client>/forgetrace_report/ \
     --config config.yaml
   ```

3. **Set Up Client Profiling**
   ```bash
   python scripts/extract_profile_samples.py \
     --input /path/to/client/repo \
     --output training/profiling_datasets/client_profile_1/ \
     --sample-size 150
   ```

---

**Deployment Time**: ~30 minutes  
**Status**: ✅ Production Ready  
**Last Updated**: 2025-11-16
