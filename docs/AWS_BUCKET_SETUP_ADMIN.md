# AWS S3 Bucket Setup Guide for Administrators

## Issue
The CI/CD IAM user `forgetrace-ci` does not have permissions to create S3 buckets due to an explicit deny policy.

## Solution
An AWS administrator needs to manually create the required S3 buckets with the following configuration.

---

## Required Buckets

### 1. Scans Bucket
**Name:** `forgetrace-scans`
**Purpose:** Store scan results, SBOMs, and audit reports

### 2. Models Bucket
**Name:** `forgetrace-models`
**Purpose:** Store ML models and MLflow artifacts

---

## Bucket Configuration

### Via AWS Console

1. **Go to S3 Console:** https://s3.console.aws.amazon.com/s3/buckets

2. **Create Bucket:** Click "Create bucket"

3. **Bucket Settings:**
   - **Bucket name:** `forgetrace-scans` (then repeat for `forgetrace-models`)
   - **Region:** `us-east-1`
   - **Block all public access:** ✅ Enable
   - **Bucket Versioning:** ✅ Enable
   - **Default encryption:** ✅ Enable (Server-side encryption with Amazon S3 managed keys - SSE-S3)

4. **Lifecycle Rules:**
   - Go to bucket → Management tab → Create lifecycle rule
   - **Rule name:** `DeleteOldVersions`
   - **Rule scope:** Apply to all objects
   - **Lifecycle rule actions:** 
     - ✅ Permanently delete noncurrent versions of objects
     - Days after objects become noncurrent: `90`
   - Create rule

5. **Bucket Policy** (optional - for additional security):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "DenyInsecureTransport",
         "Effect": "Deny",
         "Principal": "*",
         "Action": "s3:*",
         "Resource": [
           "arn:aws:s3:::forgetrace-scans",
           "arn:aws:s3:::forgetrace-scans/*"
         ],
         "Condition": {
           "Bool": {
             "aws:SecureTransport": "false"
           }
         }
       }
     ]
   }
   ```

---

## Via AWS CLI (Admin User)

```bash
# Create scans bucket
aws s3 mb s3://forgetrace-scans --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket forgetrace-scans \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket forgetrace-scans \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket forgetrace-scans \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Set lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket forgetrace-scans \
  --lifecycle-configuration '{
    "Rules": [{
      "Id": "DeleteOldVersions",
      "Status": "Enabled",
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 90
      }
    }]
  }'

# Repeat for models bucket
aws s3 mb s3://forgetrace-models --region us-east-1
aws s3api put-bucket-versioning --bucket forgetrace-models --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket forgetrace-models --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
aws s3api put-public-access-block --bucket forgetrace-models --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
aws s3api put-bucket-lifecycle-configuration --bucket forgetrace-models --lifecycle-configuration '{"Rules": [{"Id": "DeleteOldVersions", "Status": "Enabled", "NoncurrentVersionExpiration": {"NoncurrentDays": 90}}]}'
```

---

## IAM Permissions for `forgetrace-ci` User

After buckets are created, attach this policy to allow the CI/CD user to access them:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ForgeTraceS3Access",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:GetBucketVersioning",
        "s3:GetObjectVersion",
        "s3:DeleteObjectVersion"
      ],
      "Resource": [
        "arn:aws:s3:::forgetrace-scans",
        "arn:aws:s3:::forgetrace-scans/*",
        "arn:aws:s3:::forgetrace-models",
        "arn:aws:s3:::forgetrace-models/*"
      ]
    },
    {
      "Sid": "HeadBucketPermission",
      "Effect": "Allow",
      "Action": [
        "s3:HeadBucket"
      ],
      "Resource": [
        "arn:aws:s3:::forgetrace-scans",
        "arn:aws:s3:::forgetrace-models"
      ]
    }
  ]
}
```

**Policy Name:** `ForgeTraceS3AccessPolicy`

---

## Verification

After buckets are created, verify access with:

```bash
# Test bucket access
aws s3api head-bucket --bucket forgetrace-scans
aws s3api head-bucket --bucket forgetrace-models

# Test write access
echo "test" | aws s3 cp - s3://forgetrace-scans/test.txt
aws s3 ls s3://forgetrace-scans/
aws s3 rm s3://forgetrace-scans/test.txt
```

---

## Current IAM User Details

- **User:** `forgetrace-ci`
- **ARN:** `arn:aws:iam::005965605891:user/forgetrace/forgetrace-ci`
- **Account:** `005965605891`
- **Issue:** Explicit deny policy prevents bucket creation
- **Needed:** Buckets created by admin + read/write permissions granted

---

## Summary for Developer

Once the admin completes the setup:

1. ✅ Buckets `forgetrace-scans` and `forgetrace-models` will exist in `us-east-1`
2. ✅ CI/CD user will have read/write access
3. ✅ Application can upload scan results and ML models to S3
4. ✅ Run `./scripts/setup_aws.sh` again to verify access

Your AWS credentials are already configured locally - no changes needed on your end.
