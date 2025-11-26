"""
S3 Storage Service for ForgeTrace Platform
Handles artifact storage for scan results, SBOMs, and reports
"""
import json
import logging
from typing import Optional, BinaryIO
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger(__name__)


class S3StorageService:
    """Service for managing S3 artifact storage"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = None
        self.scans_bucket = settings.S3_BUCKET_SCANS
        self.models_bucket = settings.S3_BUCKET_MODELS
        
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_DEFAULT_REGION
            )
            logger.info("S3 client initialized successfully")
        else:
            logger.warning("AWS credentials not configured - S3 storage disabled")
    
    def is_enabled(self) -> bool:
        """Check if S3 storage is enabled"""
        return self.s3_client is not None
    
    async def upload_scan_result(
        self,
        tenant_id: str,
        scan_id: str,
        result_data: dict,
        content_type: str = "application/json"
    ) -> Optional[str]:
        """
        Upload scan result to S3
        
        Args:
            tenant_id: Tenant identifier for organization
            scan_id: Scan identifier
            result_data: Scan result data to upload
            content_type: MIME type of content
            
        Returns:
            S3 URL of uploaded object, or None if upload failed
        """
        if not self.is_enabled():
            logger.warning("S3 storage not enabled - skipping upload")
            return None
        
        try:
            # Create structured key path
            key = f"scans/{tenant_id}/{scan_id}/results.json"
            
            # Convert dict to JSON string
            json_data = json.dumps(result_data, indent=2)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.scans_bucket,
                Key=key,
                Body=json_data.encode('utf-8'),
                ContentType=content_type,
                Metadata={
                    'tenant_id': tenant_id,
                    'scan_id': scan_id,
                    'uploaded_at': datetime.utcnow().isoformat()
                }
            )
            
            s3_url = f"s3://{self.scans_bucket}/{key}"
            logger.info(f"Uploaded scan result to {s3_url}")
            return s3_url
            
        except ClientError as e:
            logger.error(f"Failed to upload scan result to S3: {e}")
            return None
    
    async def upload_artifact(
        self,
        tenant_id: str,
        scan_id: str,
        artifact_name: str,
        file_data: bytes,
        content_type: str = "application/octet-stream"
    ) -> Optional[str]:
        """
        Upload artifact file to S3
        
        Args:
            tenant_id: Tenant identifier
            scan_id: Scan identifier
            artifact_name: Name of artifact file
            file_data: Binary file data
            content_type: MIME type
            
        Returns:
            S3 URL of uploaded artifact
        """
        if not self.is_enabled():
            return None
        
        try:
            key = f"scans/{tenant_id}/{scan_id}/artifacts/{artifact_name}"
            
            self.s3_client.put_object(
                Bucket=self.scans_bucket,
                Key=key,
                Body=file_data,
                ContentType=content_type,
                Metadata={
                    'tenant_id': tenant_id,
                    'scan_id': scan_id
                }
            )
            
            s3_url = f"s3://{self.scans_bucket}/{key}"
            logger.info(f"Uploaded artifact to {s3_url}")
            return s3_url
            
        except ClientError as e:
            logger.error(f"Failed to upload artifact to S3: {e}")
            return None
    
    async def get_presigned_url(
        self,
        s3_url: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate presigned URL for temporary access
        
        Args:
            s3_url: S3 URL (s3://bucket/key)
            expiration: URL expiration in seconds (default 1 hour)
            
        Returns:
            Presigned HTTPS URL for download
        """
        if not self.is_enabled():
            return None
        
        try:
            # Parse S3 URL
            if not s3_url.startswith('s3://'):
                logger.error(f"Invalid S3 URL: {s3_url}")
                return None
            
            parts = s3_url[5:].split('/', 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ''
            
            # Generate presigned URL
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for {s3_url}")
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
    
    async def delete_scan_artifacts(
        self,
        tenant_id: str,
        scan_id: str
    ) -> bool:
        """
        Delete all artifacts for a scan
        
        Args:
            tenant_id: Tenant identifier
            scan_id: Scan identifier
            
        Returns:
            True if successful
        """
        if not self.is_enabled():
            return False
        
        try:
            # List all objects with prefix
            prefix = f"scans/{tenant_id}/{scan_id}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.scans_bucket,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                logger.info(f"No artifacts found for scan {scan_id}")
                return True
            
            # Delete all objects
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            
            self.s3_client.delete_objects(
                Bucket=self.scans_bucket,
                Delete={'Objects': objects_to_delete}
            )
            
            logger.info(f"Deleted {len(objects_to_delete)} artifacts for scan {scan_id}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete scan artifacts: {e}")
            return False
    
    async def create_buckets_if_not_exist(self):
        """Create S3 buckets if they don't exist (for setup)"""
        if not self.is_enabled():
            return
        
        buckets = [self.scans_bucket, self.models_bucket]
        
        for bucket in buckets:
            try:
                self.s3_client.head_bucket(Bucket=bucket)
                logger.info(f"Bucket {bucket} already exists")
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    try:
                        # Create bucket
                        if settings.AWS_DEFAULT_REGION == 'us-east-1':
                            self.s3_client.create_bucket(Bucket=bucket)
                        else:
                            self.s3_client.create_bucket(
                                Bucket=bucket,
                                CreateBucketConfiguration={
                                    'LocationConstraint': settings.AWS_DEFAULT_REGION
                                }
                            )
                        
                        # Enable versioning
                        self.s3_client.put_bucket_versioning(
                            Bucket=bucket,
                            VersioningConfiguration={'Status': 'Enabled'}
                        )
                        
                        # Set lifecycle policy for old versions
                        self.s3_client.put_bucket_lifecycle_configuration(
                            Bucket=bucket,
                            LifecycleConfiguration={
                                'Rules': [{
                                    'Id': 'DeleteOldVersions',
                                    'Status': 'Enabled',
                                    'NoncurrentVersionExpiration': {'NoncurrentDays': 90}
                                }]
                            }
                        )
                        
                        logger.info(f"Created bucket {bucket}")
                    except ClientError as create_error:
                        logger.error(f"Failed to create bucket {bucket}: {create_error}")
                else:
                    logger.error(f"Error checking bucket {bucket}: {e}")


# Global instance
s3_storage = S3StorageService()
