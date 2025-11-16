# ForgeTrace Production Infrastructure
# This Terraform configuration provisions all AWS resources needed for ForgeTrace

terraform {
  required_version = ">= 1.6.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # Uncomment for remote state (recommended for production)
  # backend "s3" {
  #   bucket         = "forgetrace-terraform-state"
  #   key            = "production/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "forgetrace-terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "ForgeTrace"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.owner_email
      CostCenter  = "Engineering"
    }
  }
}

# Generate random suffix for globally unique resource names
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# Import the ForgeTrace infrastructure module
module "forgetrace_infra" {
  source = "./modules/forgetrace-infra"
  
  environment        = var.environment
  aws_region         = var.aws_region
  owner_email        = var.owner_email
  random_suffix      = random_string.suffix.result
  
  # IAM Configuration
  ci_user_name       = var.ci_user_name
  
  # S3 Configuration
  enable_versioning  = var.enable_s3_versioning
  enable_lifecycle   = var.enable_s3_lifecycle
  glacier_days       = var.s3_glacier_transition_days
  expiration_days    = var.s3_expiration_days
  
  # CloudTrail Configuration
  enable_cloudtrail  = var.enable_cloudtrail
  
  # Monitoring
  enable_cloudwatch  = var.enable_cloudwatch
  
  # Security
  enable_encryption  = var.enable_encryption
  
  tags = var.tags
}

# Outputs for GitHub Secrets integration
output "aws_access_key_id" {
  description = "AWS Access Key ID for CI/CD (store in GitHub Secrets)"
  value       = module.forgetrace_infra.ci_user_access_key_id
  sensitive   = true
}

output "aws_secret_access_key" {
  description = "AWS Secret Access Key for CI/CD (store in GitHub Secrets)"
  value       = module.forgetrace_infra.ci_user_secret_access_key
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket name for DVC remote (store in GitHub Secrets as DVC_REMOTE_BUCKET)"
  value       = module.forgetrace_infra.s3_bucket_name
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = module.forgetrace_infra.s3_bucket_arn
}

output "cloudtrail_name" {
  description = "CloudTrail name for audit logging"
  value       = module.forgetrace_infra.cloudtrail_name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for monitoring"
  value       = module.forgetrace_infra.cloudwatch_log_group_name
}

output "deployment_summary" {
  description = "Summary of deployed resources"
  value = {
    iam_user              = module.forgetrace_infra.ci_user_name
    s3_bucket             = module.forgetrace_infra.s3_bucket_name
    cloudtrail            = module.forgetrace_infra.cloudtrail_name
    region                = var.aws_region
    environment           = var.environment
    estimated_monthly_cost = "$5-10"
  }
}

# Output formatted for easy copy-paste to GitHub Secrets
output "github_secrets_reference" {
  description = "Formatted values for GitHub Secrets configuration"
  sensitive   = true
  value = <<-EOT
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║  GitHub Secrets Configuration                                  ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    Add these secrets to your GitHub repository:
    Settings → Secrets and variables → Actions → New repository secret
    
    Secret Name: AWS_ACCESS_KEY_ID
    Value: ${module.forgetrace_infra.ci_user_access_key_id}
    
    Secret Name: AWS_SECRET_ACCESS_KEY
    Value: (marked as sensitive - use: terraform output -raw aws_secret_access_key)
    
    Secret Name: AWS_DEFAULT_REGION
    Value: ${var.aws_region}
    
    Secret Name: DVC_REMOTE_BUCKET
    Value: ${module.forgetrace_infra.s3_bucket_name}
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║  Testing AWS Connection                                        ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    export AWS_ACCESS_KEY_ID="${module.forgetrace_infra.ci_user_access_key_id}"
    export AWS_SECRET_ACCESS_KEY="(use terraform output -raw aws_secret_access_key)"
    export AWS_DEFAULT_REGION="${var.aws_region}"
    
    # Test S3 access
    aws s3 ls s3://${module.forgetrace_infra.s3_bucket_name}/
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║  Security Reminders                                            ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    ⚠️  Never commit credentials to Git
    ⚠️  Rotate credentials every 90 days (see SECURITY.md)
    ⚠️  Store credentials in password manager
    ⚠️  Enable MFA on AWS root account
    
  EOT
}
