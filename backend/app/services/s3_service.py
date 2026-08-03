import os
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    """AWS S3 Object Storage Service for video uploads."""

    def __init__(self):
        self.bucket = settings.AWS_S3_BUCKET
        self.region = settings.AWS_REGION
        self.access_key = settings.AWS_ACCESS_KEY_ID
        self.secret_key = settings.AWS_SECRET_ACCESS_KEY
        self.custom_domain = settings.AWS_S3_CUSTOM_DOMAIN

    @property
    def is_configured(self) -> bool:
        """Check if S3 bucket and credentials are set in environment."""
        return bool(self.bucket and self.access_key and self.secret_key)

    def upload_video(self, local_file_path: str, s3_key: Optional[str] = None) -> Optional[str]:
        """
        Uploads a local MP4 video file to the configured AWS S3 bucket.
        Returns the public S3 HTTP URL or custom domain URL upon success.
        If S3 is not configured or fails, returns None.
        """
        if not self.is_configured:
            logger.info("AWS S3 is not configured. Serving video from local storage endpoint.")
            return None

        if not os.path.exists(local_file_path):
            logger.error(f"Cannot upload to S3: Local file does not exist at '{local_file_path}'")
            return None

        try:
            import boto3
            from botocore.exceptions import BotoCoreError, ClientError

            s3_client = boto3.client(
                "s3",
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )

            if not s3_key:
                filename = os.path.basename(local_file_path)
                s3_key = f"videos/{filename}"

            logger.info(f"Uploading '{local_file_path}' to AWS S3 bucket '{self.bucket}' as '{s3_key}'...")

            s3_client.upload_file(
                local_file_path,
                self.bucket,
                s3_key,
                ExtraArgs={
                    "ContentType": "video/mp4",
                }
            )

            if self.custom_domain:
                url = f"https://{self.custom_domain}/{s3_key}"
            else:
                url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"

            logger.info(f"✅ S3 Upload Successful! Public URL: {url}")
            return url

        except ImportError:
            logger.warning("boto3 package is not installed. Skipping S3 upload.")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to upload video to AWS S3: {e}", exc_info=True)
            return None

s3_service = S3Service()
