# Terragrunt Root Configuration
# Shared settings across all environments

locals {
  # Parse the file path to extract environment name
  parsed = regex(".*/environments/(?P<environment>[^/]+)/.*", get_terragrunt_dir())
  environment = local.parsed.environment
}

# Remote state configuration (shared across environments)
remote_state {
  backend = "s3"
  
  config = {
    bucket         = "forgetrace-terraform-state"
    key            = "${local.environment}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "forgetrace-terraform-locks"
  }
}

# Auto-create S3 bucket and DynamoDB table for state management
# Run once before first deployment:
# aws s3 mb s3://forgetrace-terraform-state
# aws dynamodb create-table \
#   --table-name forgetrace-terraform-locks \
#   --attribute-definitions AttributeName=LockID,AttributeType=S \
#   --key-schema AttributeName=LockID,KeyType=HASH \
#   --billing-mode PAY_PER_REQUEST
