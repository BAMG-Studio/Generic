# ForgeTrace Infrastructure Module
# Provisions IAM users, S3 buckets, CloudTrail, and monitoring

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "owner_email" {
  description = "Owner email for tagging"
  type        = string
}

variable "random_suffix" {
  description = "Random suffix for globally unique names"
  type        = string
}

variable "ci_user_name" {
  description = "IAM username for CI/CD"
  type        = string
}

variable "enable_versioning" {
  description = "Enable S3 versioning"
  type        = bool
}

variable "enable_lifecycle" {
  description = "Enable S3 lifecycle policies"
  type        = bool
}

variable "glacier_days" {
  description = "Days before Glacier transition"
  type        = number
}

variable "expiration_days" {
  description = "Days before object deletion"
  type        = number
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail"
  type        = bool
}

variable "enable_cloudwatch" {
  description = "Enable CloudWatch"
  type        = bool
}

variable "enable_encryption" {
  description = "Enable encryption"
  type        = bool
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# Outputs
output "ci_user_name" {
  description = "IAM user name"
  value       = aws_iam_user.ci_user.name
}

output "ci_user_arn" {
  description = "IAM user ARN"
  value       = aws_iam_user.ci_user.arn
}

output "ci_user_access_key_id" {
  description = "Access key ID"
  value       = aws_iam_access_key.ci_user_key.id
  sensitive   = true
}

output "ci_user_secret_access_key" {
  description = "Secret access key"
  value       = aws_iam_access_key.ci_user_key.secret
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.models.id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.models.arn
}

output "cloudtrail_name" {
  description = "CloudTrail name"
  value       = var.enable_cloudtrail ? aws_cloudtrail.audit[0].name : null
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch log group name"
  value       = var.enable_cloudwatch ? aws_cloudwatch_log_group.forgetrace[0].name : null
}
