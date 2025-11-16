# ForgeTrace Terraform Infrastructure

Infrastructure-as-Code for ForgeTrace production deployment using Terraform and Terragrunt.

## 🏗️ What This Provisions

### AWS Resources
- **IAM User**: `forgetrace-ci` with scoped S3 and CloudWatch permissions
- **S3 Bucket**: Model storage with versioning, encryption, and lifecycle policies
- **CloudTrail**: Audit logging for all API calls
- **CloudWatch**: Monitoring and cost alerts
- **Folder Structure**: Auto-created folders (models/, training-data/, benchmarks/, audit-reports/, mlflow/)

### Security Features
- ✅ Encryption at rest (AES-256)
- ✅ Versioning enabled for rollback
- ✅ Public access blocked
- ✅ Audit logging via CloudTrail
- ✅ Least-privilege IAM policies
- ✅ Cost monitoring alerts

### Estimated Cost
**$5-10/month** for:
- S3 storage: $0.023/GB (~$2-5/month for 100GB)
- CloudTrail: $2/month for 1M events
- CloudWatch: $1/month for logs and alarms

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install Terraform
brew install terraform

# Install Terragrunt (optional, for multi-environment management)
brew install terragrunt

# Install AWS CLI
brew install awscli

# Configure AWS credentials (use root or admin user initially)
aws configure
```

### Option 1: Deploy with Terraform (Single Environment)

```bash
cd terraform/

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
vim terraform.tfvars

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy infrastructure
terraform apply

# Save outputs for GitHub Secrets
terraform output -json > outputs.json
terraform output github_secrets_reference
```

### Option 2: Deploy with Terragrunt (Multi-Environment)

```bash
cd terraform/environments/production/

# Initialize Terragrunt
terragrunt init

# Preview changes
terragrunt plan

# Deploy infrastructure
terragrunt apply

# Get outputs
terragrunt output github_secrets_reference
```

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare AWS Account

```bash
# Ensure you have AWS credentials configured
aws sts get-caller-identity

# Expected output: Your AWS account ID and user
```

### Step 2: Configure Variables

Edit `terraform/terraform.tfvars`:

```hcl
environment  = "production"
aws_region   = "us-east-1"  # Change to your region
owner_email  = "your-email@domain.com"

# S3 configuration
enable_s3_versioning       = true
enable_s3_lifecycle        = true
s3_glacier_transition_days = 90
s3_expiration_days         = 365

# Security
enable_cloudtrail = true
enable_cloudwatch = true
enable_encryption = true
```

### Step 3: Initialize Terraform

```bash
cd terraform/
terraform init
```

**Expected output**:
```
Initializing the backend...
Initializing modules...
Terraform has been successfully initialized!
```

### Step 4: Preview Infrastructure

```bash
terraform plan
```

**Review**:
- IAM user creation
- S3 bucket with encryption
- CloudTrail configuration
- CloudWatch alarms

### Step 5: Deploy Infrastructure

```bash
terraform apply

# Type 'yes' when prompted
```

**Deployment time**: ~2-3 minutes

### Step 6: Retrieve Credentials

```bash
# Get all outputs
terraform output

# Get specific sensitive values
terraform output -raw aws_access_key_id
terraform output -raw aws_secret_access_key

# Get formatted GitHub Secrets reference
terraform output github_secrets_reference
```

### Step 7: Add Secrets to GitHub

```bash
# Navigate to your GitHub repository
# Settings → Secrets and variables → Actions → New repository secret

# Add these secrets:
AWS_ACCESS_KEY_ID: (from terraform output)
AWS_SECRET_ACCESS_KEY: (from terraform output -raw aws_secret_access_key)
AWS_DEFAULT_REGION: us-east-1
DVC_REMOTE_BUCKET: (from terraform output s3_bucket_name)
```

---

## 🧪 Testing Deployment

### Test 1: Verify AWS Credentials

```bash
# Export credentials from Terraform outputs
export AWS_ACCESS_KEY_ID=$(terraform output -raw aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(terraform output -raw aws_secret_access_key)
export AWS_DEFAULT_REGION=$(terraform output -raw aws_region || echo "us-east-1")

# Test S3 access
BUCKET=$(terraform output -raw s3_bucket_name)
aws s3 ls s3://$BUCKET/

# Expected output: List of folders (models/, training-data/, etc.)
```

### Test 2: Upload Test File

```bash
# Create test file
echo "ForgeTrace test" > test.txt

# Upload to S3
aws s3 cp test.txt s3://$BUCKET/models/test.txt

# Verify upload
aws s3 ls s3://$BUCKET/models/

# Clean up
aws s3 rm s3://$BUCKET/models/test.txt
```

### Test 3: Verify CloudTrail

```bash
# Check CloudTrail is logging
aws cloudtrail get-trail-status \
  --name $(terraform output -raw cloudtrail_name)

# Expected output: "IsLogging": true
```

---

## 📁 Directory Structure

```
terraform/
├── main.tf                    # Root Terraform configuration
├── variables.tf               # Input variable definitions
├── terraform.tfvars.example   # Example variable values
├── terraform.tfvars           # Your actual values (gitignored)
├── outputs.tf                 # Output values
├── terragrunt.hcl             # Root Terragrunt config (optional)
│
├── modules/
│   └── forgetrace-infra/
│       ├── variables.tf       # Module variables
│       ├── iam.tf             # IAM user and policies
│       ├── s3.tf              # S3 bucket configuration
│       └── monitoring.tf      # CloudTrail and CloudWatch
│
└── environments/              # Multi-environment support (Terragrunt)
    ├── dev/
    │   └── terragrunt.hcl
    ├── staging/
    │   └── terragrunt.hcl
    └── production/
        └── terragrunt.hcl
```

---

## 🔄 Managing Infrastructure

### View Current State

```bash
# List all resources
terraform state list

# Show specific resource
terraform state show aws_s3_bucket.models

# View all outputs
terraform output
```

### Update Infrastructure

```bash
# Edit terraform.tfvars
vim terraform.tfvars

# Preview changes
terraform plan

# Apply changes
terraform apply
```

### Rotate Credentials (Every 90 Days)

```bash
# Force recreation of access key
terraform taint module.forgetrace_infra.aws_iam_access_key.ci_user_key

# Apply to rotate credentials
terraform apply

# Update GitHub Secrets immediately
terraform output -raw aws_secret_access_key
```

### Destroy Infrastructure (Cleanup)

```bash
# ⚠️ WARNING: This deletes ALL resources

# Preview what will be deleted
terraform plan -destroy

# Delete infrastructure
terraform destroy

# Type 'yes' to confirm
```

---

## 🛡️ Security Best Practices

### 1. Protect Terraform State

```bash
# Never commit terraform.tfstate to Git
echo "terraform.tfstate*" >> .gitignore
echo "terraform.tfvars" >> .gitignore

# Use remote state in production
# See terraform/main.tf backend configuration
```

### 2. Rotate Credentials Regularly

```bash
# Set calendar reminder for every 90 days
# Rotation command:
terraform taint module.forgetrace_infra.aws_iam_access_key.ci_user_key
terraform apply
```

### 3. Enable MFA on Root Account

```bash
# AWS Console → IAM → Users → root
# → Security credentials → Activate MFA
```

### 4. Review CloudTrail Logs Monthly

```bash
# Download recent logs
BUCKET=$(terraform output -raw cloudtrail_bucket_name)
aws s3 sync s3://$BUCKET/AWSLogs/ ./audit-logs/ --exclude "*" --include "*$(date +%Y/%m/%d)*"
```

---

## 🐛 Troubleshooting

### Issue: "Access Denied" during terraform apply

**Cause**: Insufficient AWS permissions

**Solution**:
```bash
# Ensure your AWS user has these policies:
# - IAMFullAccess
# - AmazonS3FullAccess
# - CloudTrailFullAccess
# - CloudWatchFullAccess

# Or use AdministratorAccess temporarily
aws iam list-attached-user-policies --user-name $(aws sts get-caller-identity --query Arn --output text | cut -d'/' -f2)
```

### Issue: "Bucket name already exists"

**Cause**: S3 bucket names are globally unique

**Solution**:
```bash
# Terraform auto-generates unique names with random suffix
# If still failing, manually set in terraform.tfvars:
# random_suffix = "yourname-2025"
```

### Issue: "Backend initialization required"

**Cause**: Remote state bucket doesn't exist

**Solution**:
```bash
# Create S3 bucket for state
aws s3 mb s3://forgetrace-terraform-state

# Create DynamoDB table for locking
aws dynamodb create-table \
  --table-name forgetrace-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Issue: "Invalid AWS credentials"

**Solution**:
```bash
# Verify credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

---

## 📊 Cost Optimization

### Monitor Monthly Costs

```bash
# Check S3 storage size
aws s3api list-objects-v2 --bucket $(terraform output -raw s3_bucket_name) \
  --query 'sum(Contents[].Size)' --output text | numfmt --to=iec

# Expected: <100 GB = ~$2.30/month
```

### Lifecycle Policy Savings

- **Day 0-90**: Standard storage ($0.023/GB)
- **Day 90-365**: Glacier storage ($0.004/GB) → **83% savings**
- **Day 365+**: Deleted → **100% savings**

**Estimated savings**: $100-200/year on model storage

---

## 🔗 Integration with ForgeTrace

### Update DVC Configuration

```bash
# After Terraform deployment, update .dvc/config
dvc remote add -d storage s3://$(terraform output -raw s3_bucket_name)/dvc-cache
dvc remote modify storage region us-east-1

# Test DVC push
dvc push
```

### Update MLflow Configuration

```bash
# In docker-compose.yml or .env
MLFLOW_S3_ENDPOINT_URL=https://s3.amazonaws.com
AWS_ACCESS_KEY_ID=$(terraform output -raw aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(terraform output -raw aws_secret_access_key)
```

---

## 📚 Additional Resources

- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- **Terragrunt Documentation**: https://terragrunt.gruntwork.io/
- **AWS IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **ForgeTrace QUICKSTART**: `../QUICKSTART.md`
- **ForgeTrace SECURITY**: `../SECURITY.md`

---

## 🎯 Next Steps

After successful deployment:

1. ✅ **Test AWS credentials** (see Testing section)
2. ✅ **Add secrets to GitHub** (see Step 7)
3. ✅ **Deploy MLflow** (see `../QUICKSTART.md`)
4. ✅ **Run test audit** (verify S3 integration)
5. ✅ **Set up monitoring** (CloudWatch dashboard)

**Estimated time to production**: 30 minutes after Terraform deployment

---

**Created**: 2025-11-16  
**Status**: ✅ Ready for Deployment  
**Maintainer**: peter@beaconagile.net
