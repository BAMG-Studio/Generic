# S3 Bucket for Model Storage
# Stores ML models, training data, benchmarks, and audit reports

locals {
  bucket_name = "forgetrace-models-${var.environment}-${var.random_suffix}"
}

resource "aws_s3_bucket" "models" {
  bucket = local.bucket_name
  
  tags = merge(
    var.tags,
    {
      Name        = local.bucket_name
      Purpose     = "ML Model Storage and Artifacts"
      Environment = var.environment
      CreatedBy   = "Terraform"
    }
  )
}

# Enable versioning for rollback capability
resource "aws_s3_bucket_versioning" "models" {
  bucket = aws_s3_bucket.models.id
  
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "models" {
  count  = var.enable_encryption ? 1 : 0
  bucket = aws_s3_bucket.models.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Block all public access (critical for security)
resource "aws_s3_bucket_public_access_block" "models" {
  bucket = aws_s3_bucket.models.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy for cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "models" {
  count  = var.enable_lifecycle ? 1 : 0
  bucket = aws_s3_bucket.models.id
  
  # Archive old models to Glacier
  rule {
    id     = "archive-old-models"
    status = "Enabled"
    
    filter {
      prefix = "models/"
    }
    
    transition {
      days          = var.glacier_days
      storage_class = "GLACIER"
    }
    
    expiration {
      days = var.expiration_days
    }
    
    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }
    
    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
  
  # Clean up incomplete multipart uploads (saves costs)
  rule {
    id     = "cleanup-incomplete-uploads"
    status = "Enabled"
    
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
  
  # Archive training data after 180 days
  rule {
    id     = "archive-training-data"
    status = "Enabled"
    
    filter {
      prefix = "training-data/"
    }
    
    transition {
      days          = 180
      storage_class = "GLACIER_IR"
    }
  }
  
  # Keep benchmarks for 1 year, then delete
  rule {
    id     = "expire-old-benchmarks"
    status = "Enabled"
    
    filter {
      prefix = "benchmarks/"
    }
    
    expiration {
      days = 365
    }
  }
}

# Create folder structure using S3 objects
resource "aws_s3_object" "folder_models" {
  bucket = aws_s3_bucket.models.id
  key    = "models/"
  
  tags = {
    Purpose = "ML model artifacts"
  }
}

resource "aws_s3_object" "folder_training_data" {
  bucket = aws_s3_bucket.models.id
  key    = "training-data/"
  
  tags = {
    Purpose = "Training datasets"
  }
}

resource "aws_s3_object" "folder_benchmarks" {
  bucket = aws_s3_bucket.models.id
  key    = "benchmarks/"
  
  tags = {
    Purpose = "Performance benchmarks"
  }
}

resource "aws_s3_object" "folder_audit_reports" {
  bucket = aws_s3_bucket.models.id
  key    = "audit-reports/"
  
  tags = {
    Purpose = "Repository audit reports"
  }
}

resource "aws_s3_object" "folder_mlflow" {
  bucket = aws_s3_bucket.models.id
  key    = "mlflow/"
  
  tags = {
    Purpose = "MLflow experiment artifacts"
  }
}

# Bucket policy for MLflow access (if needed)
resource "aws_s3_bucket_policy" "models" {
  bucket = aws_s3_bucket.models.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyInsecureTransport"
        Effect = "Deny"
        Principal = "*"
        Action = "s3:*"
        Resource = [
          aws_s3_bucket.models.arn,
          "${aws_s3_bucket.models.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}
