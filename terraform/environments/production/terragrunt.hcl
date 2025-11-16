# Terragrunt Configuration for ForgeTrace
# Manages multiple environments (dev, staging, production)

# Include root terragrunt configuration
include "root" {
  path = find_in_parent_folders()
}

# Environment-specific variables
locals {
  environment = "production"
  aws_region  = "us-east-1"
}

# Terraform source
terraform {
  source = "../../"
}

# Input variables for this environment
inputs = {
  environment  = local.environment
  aws_region   = local.aws_region
  owner_email  = "peter@beaconagile.net"
  ci_user_name = "forgetrace-ci-${local.environment}"
  
  # S3 configuration
  enable_s3_versioning       = true
  enable_s3_lifecycle        = true
  s3_glacier_transition_days = 90
  s3_expiration_days         = 365
  
  # Security & monitoring
  enable_cloudtrail = true
  enable_cloudwatch = true
  enable_encryption = true
  
  # Tags
  tags = {
    Environment = local.environment
    ManagedBy   = "Terragrunt"
    Team        = "DevOps"
  }
}

# Remote state configuration (S3 + DynamoDB locking)
remote_state {
  backend = "s3"
  
  config = {
    bucket         = "forgetrace-terraform-state-${local.environment}"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = local.aws_region
    encrypt        = true
    dynamodb_table = "forgetrace-terraform-locks"
  }
  
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

# Provider configuration
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  
  contents = <<EOF
provider "aws" {
  region = "${local.aws_region}"
  
  default_tags {
    tags = {
      Environment = "${local.environment}"
      ManagedBy   = "Terragrunt"
    }
  }
}
EOF
}
