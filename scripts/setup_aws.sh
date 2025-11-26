#!/bin/bash
# AWS S3 Setup Script for ForgeTrace Platform
# Creates S3 buckets for scan artifacts and ML models (or verifies existing access)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}ForgeTrace AWS S3 Setup${NC}"
echo "================================"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install with: pip install awscli"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Configure with: aws configure"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI configured${NC}"

# Get current IAM user/role
IDENTITY=$(aws sts get-caller-identity --output json 2>/dev/null)
USER_ARN=$(echo "$IDENTITY" | grep -o '"Arn": "[^"]*"' | cut -d'"' -f4)
echo -e "${BLUE}Current identity: $USER_ARN${NC}"

# Read bucket names from .env or use defaults
SCANS_BUCKET=${S3_BUCKET_SCANS:-"forgetrace-scans"}
MODELS_BUCKET=${S3_BUCKET_MODELS:-"forgetrace-models"}
REGION=${AWS_DEFAULT_REGION:-"us-east-1"}

echo ""
echo "Bucket Configuration:"
echo "  Scans Bucket: $SCANS_BUCKET"
echo "  Models Bucket: $MODELS_BUCKET"
echo "  Region: $REGION"
echo ""

# Function to create or verify bucket access
create_or_verify_bucket() {
    local bucket=$1
    local region=$2
    
    echo ""
    echo -e "${BLUE}Checking bucket: $bucket${NC}"
    
    # Try to access bucket (more permissive than listing all buckets)
    if aws s3api head-bucket --bucket "$bucket" 2>/dev/null; then
        echo -e "${GREEN}✓ Bucket $bucket exists and is accessible${NC}"
        
        # Test write permission
        TEST_KEY="forgetrace-test-$(date +%s).txt"
        if echo "test" | aws s3 cp - "s3://$bucket/$TEST_KEY" 2>/dev/null; then
            echo -e "${GREEN}✓ Write access confirmed${NC}"
            aws s3 rm "s3://$bucket/$TEST_KEY" 2>/dev/null
        else
            echo -e "${YELLOW}⚠ Limited permissions - read-only access${NC}"
        fi
        return 0
    fi
    
    # Bucket doesn't exist, try to create it
    echo "Creating bucket: $bucket"
    
    # Create bucket (different command for us-east-1)
    if [ "$region" = "us-east-1" ]; then
        if aws s3 mb "s3://$bucket" --region "$region" 2>/dev/null; then
            echo -e "${GREEN}✓ Bucket created${NC}"
        else
            echo -e "${RED}✗ Failed to create bucket${NC}"
            echo -e "${YELLOW}Note: Bucket may need to be created by an admin${NC}"
            return 1
        fi
    else
        if aws s3 mb "s3://$bucket" --region "$region" --create-bucket-configuration LocationConstraint="$region" 2>/dev/null; then
            echo -e "${GREEN}✓ Bucket created${NC}"
        else
            echo -e "${RED}✗ Failed to create bucket${NC}"
            echo -e "${YELLOW}Note: Bucket may need to be created by an admin${NC}"
            return 1
        fi
    fi
    
    # Try to enable versioning (may not have permission)
    echo "  Configuring bucket settings..."
    if aws s3api put-bucket-versioning \
        --bucket "$bucket" \
        --versioning-configuration Status=Enabled 2>/dev/null; then
        echo -e "${GREEN}  ✓ Versioning enabled${NC}"
    else
        echo -e "${YELLOW}  ⚠ Could not enable versioning (may require admin)${NC}"
    fi
    
    # Try to set lifecycle policy
    if aws s3api put-bucket-lifecycle-configuration \
        --bucket "$bucket" \
        --lifecycle-configuration '{
            "Rules": [{
                "Id": "DeleteOldVersions",
                "Status": "Enabled",
                "NoncurrentVersionExpiration": {
                    "NoncurrentDays": 90
                }
            }]
        }' 2>/dev/null; then
        echo -e "${GREEN}  ✓ Lifecycle policy set${NC}"
    else
        echo -e "${YELLOW}  ⚠ Could not set lifecycle policy (may require admin)${NC}"
    fi
    
    # Try to enable server-side encryption
    if aws s3api put-bucket-encryption \
        --bucket "$bucket" \
        --server-side-encryption-configuration '{
            "Rules": [{
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }]
        }' 2>/dev/null; then
        echo -e "${GREEN}  ✓ Encryption enabled${NC}"
    else
        echo -e "${YELLOW}  ⚠ Could not enable encryption (may require admin)${NC}"
    fi
    
    # Try to block public access
    if aws s3api put-public-access-block \
        --bucket "$bucket" \
        --public-access-block-configuration \
            "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" 2>/dev/null; then
        echo -e "${GREEN}  ✓ Public access blocked${NC}"
    else
        echo -e "${YELLOW}  ⚠ Could not block public access (may require admin)${NC}"
    fi
}

# Create or verify buckets
echo ""
echo "Setting up S3 buckets..."
echo "================================"

SCANS_SUCCESS=0
MODELS_SUCCESS=0

if create_or_verify_bucket "$SCANS_BUCKET" "$REGION"; then
    SCANS_SUCCESS=1
fi

if create_or_verify_bucket "$MODELS_BUCKET" "$REGION"; then
    MODELS_SUCCESS=1
fi

echo ""
echo "================================"
echo -e "${BLUE}Setup Summary${NC}"
echo "================================"

if [ $SCANS_SUCCESS -eq 1 ]; then
    echo -e "${GREEN}✓ Scans bucket ($SCANS_BUCKET) ready${NC}"
else
    echo -e "${RED}✗ Scans bucket ($SCANS_BUCKET) - needs admin setup${NC}"
fi

if [ $MODELS_SUCCESS -eq 1 ]; then
    echo -e "${GREEN}✓ Models bucket ($MODELS_BUCKET) ready${NC}"
else
    echo -e "${RED}✗ Models bucket ($MODELS_BUCKET) - needs admin setup${NC}"
fi

echo ""
if [ $SCANS_SUCCESS -eq 1 ] && [ $MODELS_SUCCESS -eq 1 ]; then
    echo -e "${GREEN}✓ S3 setup complete!${NC}"
    echo ""
    echo "AWS credentials are already configured."
    echo "Your backend/.env should have:"
    echo "  AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
    echo "  AWS_SECRET_ACCESS_KEY=***"
    echo "  AWS_DEFAULT_REGION=$REGION"
    echo "  S3_BUCKET_SCANS=$SCANS_BUCKET"
    echo "  S3_BUCKET_MODELS=$MODELS_BUCKET"
    echo ""
    echo "Test S3 access:"
    echo "  aws s3api head-bucket --bucket $SCANS_BUCKET"
else
    echo -e "${YELLOW}⚠ Partial setup - some buckets need admin access${NC}"
    echo ""
    echo "Contact your AWS administrator to create the missing buckets:"
    [ $SCANS_SUCCESS -eq 0 ] && echo "  - $SCANS_BUCKET"
    [ $MODELS_SUCCESS -eq 0 ] && echo "  - $MODELS_BUCKET"
    echo ""
    echo "Required bucket settings:"
    echo "  - Region: $REGION"
    echo "  - Versioning: Enabled"
    echo "  - Encryption: AES256"
    echo "  - Public access: Blocked"
    echo "  - Lifecycle: Delete old versions after 90 days"
    echo ""
    echo "IAM permissions needed for CI/CD user:"
    echo "  - s3:PutObject, s3:GetObject, s3:DeleteObject"
    echo "  - s3:ListBucket"
fi
echo ""
