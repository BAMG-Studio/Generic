# CloudTrail for Audit Logging
# Tracks all API calls for security and compliance

resource "aws_s3_bucket" "cloudtrail_logs" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = "forgetrace-cloudtrail-${var.environment}-${var.random_suffix}"
  
  tags = merge(
    var.tags,
    {
      Name        = "forgetrace-cloudtrail-${var.environment}"
      Purpose     = "CloudTrail Audit Logs"
      Environment = var.environment
    }
  )
}

resource "aws_s3_bucket_public_access_block" "cloudtrail_logs" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail_logs[0].id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail_logs[0].id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs[0].arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs[0].arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

resource "aws_cloudtrail" "audit" {
  count                         = var.enable_cloudtrail ? 1 : 0
  name                          = "forgetrace-audit-${var.environment}"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs[0].id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  
  event_selector {
    read_write_type           = "All"
    include_management_events = true
    
    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.models.arn}/"]
    }
  }
  
  tags = merge(
    var.tags,
    {
      Name        = "forgetrace-audit-${var.environment}"
      Purpose     = "Security Audit Trail"
      Environment = var.environment
    }
  )
  
  depends_on = [aws_s3_bucket_policy.cloudtrail_logs]
}

# CloudWatch Log Group for ForgeTrace
resource "aws_cloudwatch_log_group" "forgetrace" {
  count             = var.enable_cloudwatch ? 1 : 0
  name              = "/forgetrace/${var.environment}"
  retention_in_days = 30  # Keep logs for 30 days
  
  tags = merge(
    var.tags,
    {
      Name        = "forgetrace-logs-${var.environment}"
      Purpose     = "Application Monitoring"
      Environment = var.environment
    }
  )
}

# CloudWatch Metric Alarm for S3 bucket size (cost monitoring)
resource "aws_cloudwatch_metric_alarm" "s3_bucket_size" {
  count               = var.enable_cloudwatch ? 1 : 0
  alarm_name          = "forgetrace-s3-size-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "BucketSizeBytes"
  namespace           = "AWS/S3"
  period              = 86400  # 24 hours
  statistic           = "Average"
  threshold           = 10737418240  # 10 GB
  alarm_description   = "Alert when S3 bucket exceeds 10GB"
  
  dimensions = {
    BucketName = aws_s3_bucket.models.id
    StorageType = "StandardStorage"
  }
  
  tags = var.tags
}

# CloudWatch Metric Alarm for unusual API call patterns
resource "aws_cloudwatch_metric_alarm" "unusual_api_calls" {
  count               = var.enable_cloudwatch && var.enable_cloudtrail ? 1 : 0
  alarm_name          = "forgetrace-unusual-api-calls-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CallCount"
  namespace           = "AWS/S3"
  period              = 300  # 5 minutes
  statistic           = "Sum"
  threshold           = 1000  # Alert if >1000 API calls in 5 minutes
  alarm_description   = "Alert on unusual S3 API call volume"
  
  dimensions = {
    BucketName = aws_s3_bucket.models.id
  }
  
  tags = var.tags
}
