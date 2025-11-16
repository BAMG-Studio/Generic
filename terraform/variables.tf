# Variables for ForgeTrace Infrastructure

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "owner_email" {
  description = "Email of infrastructure owner (for tagging and notifications)"
  type        = string
  default     = "peter@beaconagile.net"
}

variable "ci_user_name" {
  description = "IAM username for CI/CD pipeline"
  type        = string
  default     = "forgetrace-ci"
}

# S3 Configuration
variable "enable_s3_versioning" {
  description = "Enable versioning on S3 bucket"
  type        = bool
  default     = true
}

variable "enable_s3_lifecycle" {
  description = "Enable lifecycle policies for cost optimization"
  type        = bool
  default     = true
}

variable "s3_glacier_transition_days" {
  description = "Days before transitioning objects to Glacier"
  type        = number
  default     = 90
}

variable "s3_expiration_days" {
  description = "Days before deleting old objects"
  type        = number
  default     = 365
}

# Security & Monitoring
variable "enable_cloudtrail" {
  description = "Enable CloudTrail audit logging"
  type        = bool
  default     = true
}

variable "enable_cloudwatch" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "enable_encryption" {
  description = "Enable encryption at rest for S3"
  type        = bool
  default     = true
}

# Tagging
variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}
