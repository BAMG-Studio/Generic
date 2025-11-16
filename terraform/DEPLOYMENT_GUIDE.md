# ForgeTrace Infrastructure Deployment - Quick Reference

## ✅ What's Been Automated

All AWS infrastructure provisioning is now **fully automated** with Terraform/Terragrunt:

### Automated Resources
- ✅ IAM user (`forgetrace-ci`) with scoped permissions
- ✅ S3 bucket with encryption, versioning, lifecycle policies
- ✅ CloudTrail audit logging (all regions)
- ✅ CloudWatch monitoring and cost alerts
- ✅ Folder structure (models/, training-data/, benchmarks/, mlflow/)

### Manual Steps Remaining
- GitHub Token generation (5 minutes)
- MLflow deployment (10 minutes via Docker Compose)
- GitHub Secrets configuration (10 minutes)

---

## 🚀 30-Minute Deployment Path

### Step 1: Deploy AWS Infrastructure (10 minutes)

```bash
cd terraform/

# One-command deployment
./deploy.sh full

# This will:
# 1. Check prerequisites (Terraform, AWS CLI)
# 2. Verify AWS credentials
# 3. Create terraform.tfvars from example
# 4. Initialize Terraform
# 5. Plan infrastructure changes
# 6. Apply (after your confirmation)
# 7. Test deployment
# 8. Display outputs for GitHub Secrets
```

**What you'll get**:
```
✅ IAM user: forgetrace-ci
✅ S3 bucket: forgetrace-models-production-abc12345
✅ Access Key ID: AKIA...
✅ Secret Access Key: (saved in Terraform state)
✅ CloudTrail: forgetrace-audit-production
✅ CloudWatch: /forgetrace/production
```

### Step 2: Generate GitHub Token (5 minutes)

```bash
# Navigate to: https://github.com/settings/tokens
# Click: Generate new token (classic)
# Scopes: 
#   ✅ repo (all)
#   ✅ workflow
#   ✅ write:packages

# Save token: ghp_xxxxxxxxxxxxxxxxxxxx
```

### Step 3: Add GitHub Secrets (10 minutes)

```bash
# Navigate to: https://github.com/BAMG-Studio/Generic/settings/secrets/actions

# Add these 8 secrets (from Terraform outputs):
terraform output github_secrets_reference

# Copy-paste values:
AWS_ACCESS_KEY_ID: (from output)
AWS_SECRET_ACCESS_KEY: (from output)
AWS_DEFAULT_REGION: us-east-1
DVC_REMOTE_BUCKET: (from output)
GITHUB_TOKEN: ghp_...
MLFLOW_TRACKING_URI: http://localhost:5000
MLFLOW_USERNAME: admin (optional)
MLFLOW_PASSWORD: (set your password)
```

### Step 4: Deploy MLflow (5 minutes)

```bash
# Already configured in docker-compose.yml
cd ..

# Create .env file with Terraform outputs
cat > .env << EOF
AWS_ACCESS_KEY_ID=$(cd terraform && terraform output -raw aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(cd terraform && terraform output -raw aws_secret_access_key)
AWS_DEFAULT_REGION=us-east-1
DVC_REMOTE_BUCKET=$(cd terraform && terraform output -raw s3_bucket_name)
MLFLOW_DB_PASSWORD=change_this_password_123
EOF

# Start MLflow
docker-compose up -d

# Verify
curl http://localhost:5000/api/2.0/mlflow/experiments/list
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] AWS account with billing enabled
- [ ] AWS CLI installed and configured
- [ ] Terraform installed (>= 1.6.0)
- [ ] Docker and Docker Compose installed
- [ ] GitHub admin access to repository

### AWS Infrastructure (Automated)
- [ ] Run `cd terraform && ./deploy.sh full`
- [ ] Verify IAM user created
- [ ] Verify S3 bucket accessible
- [ ] Save Terraform outputs

### GitHub Configuration (Manual)
- [ ] Generate GitHub personal access token
- [ ] Add 8 secrets to repository
- [ ] Run "Test Secrets" workflow
- [ ] Verify secrets are accessible

### MLflow Deployment (Semi-Automated)
- [ ] Create .env file with AWS credentials
- [ ] Run `docker-compose up -d`
- [ ] Access MLflow UI: http://localhost:5000
- [ ] Test artifact upload to S3

### Validation
- [ ] Run local audit: `forgetrace audit test_output/ml_demo_repo/`
- [ ] Verify S3 upload works
- [ ] Create test PR
- [ ] Verify CI/CD pipeline runs
- [ ] Check CloudTrail logs

---

## 🔧 Terraform Commands Reference

### Common Operations

```bash
cd terraform/

# Initialize
./deploy.sh init

# Preview changes
./deploy.sh plan

# Apply changes
./deploy.sh apply

# Test deployment
./deploy.sh test

# Display outputs
./deploy.sh outputs

# Full deployment
./deploy.sh full

# Destroy everything (⚠️ DANGER)
./deploy.sh destroy
```

### Manual Terraform Commands

```bash
cd terraform/

# Get specific output
terraform output -raw aws_access_key_id
terraform output -raw aws_secret_access_key
terraform output -raw s3_bucket_name

# Rotate credentials (every 90 days)
terraform taint module.forgetrace_infra.aws_iam_access_key.ci_user_key
terraform apply

# Update infrastructure
vim terraform.tfvars
terraform plan
terraform apply
```

---

## 💰 Cost Breakdown

### Monthly Estimate: $5-10

| Service | Usage | Cost |
|---------|-------|------|
| S3 Standard Storage | 100 GB | $2.30 |
| S3 Glacier Storage | 500 GB (after 90 days) | $2.00 |
| CloudTrail | 1M events/month | $2.00 |
| CloudWatch Logs | 5 GB/month | $0.50 |
| CloudWatch Alarms | 2 alarms | $0.20 |
| **Total** | | **$7.00/month** |

### Cost Optimization

```hcl
# terraform.tfvars
s3_glacier_transition_days = 90   # Archive after 90 days → 83% savings
s3_expiration_days = 365          # Delete after 1 year → 100% savings
```

**Estimated annual savings**: $100-200 from lifecycle policies

---

## 🛡️ Security Highlights

### Automated Security Features

- ✅ **Encryption at rest**: AES-256 for all S3 objects
- ✅ **Public access blocked**: All S3 buckets private
- ✅ **Audit logging**: CloudTrail tracks all API calls
- ✅ **Least privilege IAM**: Scoped to specific bucket only
- ✅ **Versioning enabled**: Rollback capability for models
- ✅ **HTTPS enforced**: Deny non-SSL transport

### Security Compliance Checklist

```bash
# Verify security settings
cd terraform/

# Check IAM policies
terraform state show module.forgetrace_infra.aws_iam_policy.s3_forgetrace_access

# Check S3 public access block
terraform state show module.forgetrace_infra.aws_s3_bucket_public_access_block.models

# Check CloudTrail status
aws cloudtrail get-trail-status \
  --name $(terraform output -raw cloudtrail_name)
```

### Credential Rotation Schedule

```bash
# Every 90 days (automated reminder)
terraform taint module.forgetrace_infra.aws_iam_access_key.ci_user_key
terraform apply

# Update GitHub Secrets immediately
terraform output -raw aws_secret_access_key
# → Copy to GitHub Secrets → AWS_SECRET_ACCESS_KEY
```

---

## 🐛 Troubleshooting

### Issue: "AWS credentials not configured"

```bash
# Configure AWS CLI
aws configure

# Test connection
aws sts get-caller-identity
```

### Issue: "Terraform not found"

```bash
# Install Terraform
brew install terraform

# Verify installation
terraform version
```

### Issue: "S3 bucket already exists"

```bash
# Terraform auto-generates unique names
# If collision, manually set suffix in terraform.tfvars:
random_suffix = "yourinitials-2025"
```

### Issue: "Permission denied: deploy.sh"

```bash
chmod +x terraform/deploy.sh
```

### Issue: "CloudTrail creation failed"

```bash
# Create CloudTrail bucket manually first
aws s3 mb s3://forgetrace-cloudtrail-$(uuidgen | tr '[:upper:]' '[:lower:]')

# Then re-run Terraform
terraform apply
```

---

## 📊 Monitoring

### CloudWatch Alarms (Automated)

```bash
# Check alarm status
aws cloudwatch describe-alarms \
  --alarm-names "forgetrace-s3-size-production"

# Triggered when:
# - S3 bucket > 10 GB
# - Unusual API call volume (>1000 calls/5min)
```

### Cost Monitoring

```bash
# Check S3 bucket size
aws s3api list-objects-v2 \
  --bucket $(cd terraform && terraform output -raw s3_bucket_name) \
  --query 'sum(Contents[].Size)' | numfmt --to=iec

# Check CloudTrail events
aws cloudtrail lookup-events --max-results 10
```

---

## 🎯 What's Next After Deployment

### Immediate (Today)
1. ✅ Run `terraform/deploy.sh full`
2. ✅ Generate GitHub token
3. ✅ Add GitHub Secrets
4. ✅ Deploy MLflow
5. ✅ Test local audit

### Short-term (This Week)
1. Run ML training pipeline
2. Create test PR and verify CI/CD
3. Set up CloudWatch dashboard
4. Review SECURITY.md and set rotation reminders

### Long-term (This Month)
1. Extract client profiling datasets
2. Run performance benchmarks
3. Enable branch protection
4. Set up monitoring alerts

---

## 📚 Documentation Index

| Document | Purpose | Time |
|----------|---------|------|
| `terraform/README.md` | Complete Terraform guide | Reference |
| `QUICKSTART.md` | 30-minute deployment | 30 min |
| `NEXT_STEPS.md` | Step-by-step next actions | Reference |
| `SECURITY.md` | Security policies | Reference |
| `docs/DEPLOYMENT_CHECKLIST.md` | Detailed checklist | 1-2 hours |
| `docs/PRODUCTION_DEPLOYMENT.md` | Full deployment guide | Reference |

---

## ✨ Summary

**Before Terraform**: 1-2 hours of manual AWS console clicking  
**With Terraform**: 10 minutes + 1 command (`./deploy.sh full`)

**Automated**:
- IAM user creation
- S3 bucket configuration  
- CloudTrail setup
- CloudWatch monitoring
- Security policies

**Manual (cannot automate)**:
- GitHub token generation (security requirement)
- GitHub Secrets configuration (requires repo admin)
- MLflow deployment (local Docker)

**Total time to production**: 30 minutes

---

**Created**: 2025-11-16  
**Status**: ✅ Production Ready  
**Next Action**: `cd terraform && ./deploy.sh full`
