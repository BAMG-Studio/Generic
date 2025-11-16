# IAM User for CI/CD Pipeline
# Creates a dedicated user with minimal required permissions

resource "aws_iam_user" "ci_user" {
  name = var.ci_user_name
  path = "/forgetrace/"
  
  tags = merge(
    var.tags,
    {
      Name        = var.ci_user_name
      Purpose     = "CI/CD Pipeline Automation"
      Environment = var.environment
      CreatedBy   = "Terraform"
    }
  )
}

# Access key for programmatic access
resource "aws_iam_access_key" "ci_user_key" {
  user = aws_iam_user.ci_user.name
}

# S3 Full Access Policy (scoped to ForgeTrace bucket only)
resource "aws_iam_policy" "s3_forgetrace_access" {
  name        = "ForgeTraceS3Access-${var.environment}"
  description = "Full access to ForgeTrace S3 bucket for model storage"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ListBucket"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:ListBucketMultipartUploads"
        ]
        Resource = aws_s3_bucket.models.arn
      },
      {
        Sid    = "ObjectAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetObjectVersion",
          "s3:ListMultipartUploadParts",
          "s3:AbortMultipartUpload"
        ]
        Resource = "${aws_s3_bucket.models.arn}/*"
      }
    ]
  })
  
  tags = var.tags
}

# CloudWatch Logs Access Policy
resource "aws_iam_policy" "cloudwatch_logs_access" {
  name        = "ForgeTraceCloudWatchAccess-${var.environment}"
  description = "Write access to CloudWatch Logs for monitoring"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CloudWatchLogsAccess"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = var.enable_cloudwatch ? "${aws_cloudwatch_log_group.forgetrace[0].arn}:*" : "*"
      }
    ]
  })
  
  tags = var.tags
}

# Attach S3 policy to CI user
resource "aws_iam_user_policy_attachment" "ci_user_s3" {
  user       = aws_iam_user.ci_user.name
  policy_arn = aws_iam_policy.s3_forgetrace_access.arn
}

# Attach CloudWatch policy to CI user
resource "aws_iam_user_policy_attachment" "ci_user_cloudwatch" {
  user       = aws_iam_user.ci_user.name
  policy_arn = aws_iam_policy.cloudwatch_logs_access.arn
}

# Optional: Read-only access to CloudTrail for audit purposes
resource "aws_iam_user_policy_attachment" "ci_user_cloudtrail_readonly" {
  count = var.enable_cloudtrail ? 1 : 0
  
  user       = aws_iam_user.ci_user.name
  policy_arn = "arn:aws:iam::aws:policy/CloudTrailReadOnlyAccess"
}

# Security: Force MFA after initial setup (optional, commented out)
# Uncomment to enforce MFA for CI user
# resource "aws_iam_user_policy" "force_mfa" {
#   name = "ForceMFA"
#   user = aws_iam_user.ci_user.name
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Sid       = "DenyAllExceptListedIfNoMFA"
#         Effect    = "Deny"
#         NotAction = [
#           "iam:CreateVirtualMFADevice",
#           "iam:EnableMFADevice",
#           "iam:GetUser",
#           "iam:ListMFADevices",
#           "iam:ListVirtualMFADevices",
#           "iam:ResyncMFADevice",
#           "sts:GetSessionToken"
#         ]
#         Resource = "*"
#         Condition = {
#           BoolIfExists = {
#             "aws:MultiFactorAuthPresent" = "false"
#           }
#         }
#       }
#     ]
#   })
# }
