import os
import logging
from typing import Optional
from app.core.config import settings

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class S3Service:
    """AWS S3 Object Storage Service for video uploads."""

    @property
    def bucket(self) -> str:
        return settings.AWS_S3_BUCKET

    @property
    def region(self) -> str:
        return settings.AWS_REGION

    @property
    def access_key(self) -> str:
        return settings.AWS_ACCESS_KEY_ID

    @property
    def secret_key(self) -> str:
        return settings.AWS_SECRET_ACCESS_KEY

    @property
    def custom_domain(self) -> str:
        return settings.AWS_S3_CUSTOM_DOMAIN

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
            logger.info("ℹ️  [S3] Not configured — skipping upload. Videos served from local storage.")
            return None

        # Resolve absolute path in case a relative path was returned by the pipeline
        abs_file_path = os.path.abspath(local_file_path)

        if not os.path.exists(abs_file_path):
            logger.error(f"❌ [S3] Cannot upload — local file does NOT exist at: '{abs_file_path}'")
            return None

        file_size_bytes = os.path.getsize(abs_file_path)
        if file_size_bytes == 0:
            logger.error(f"❌ [S3] Cannot upload — file is empty (0 bytes) at: '{abs_file_path}'")
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
                filename = os.path.basename(abs_file_path)
                s3_key = f"videos/{filename}"

            logger.info(
                f"☁️  [S3] Uploading → '{s3_key}' to bucket '{self.bucket}' "
                f"({file_size_bytes:,} bytes / {file_size_bytes / 1024:.1f} KB) ..."
            )

            s3_client.upload_file(
                abs_file_path,
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

            logger.info(f"✅ [S3] Upload complete! Public URL: {url}")
            return url

        except ImportError:
            logger.error("❌ [S3] boto3 not installed. Run: pip install boto3")
            return None
        except Exception as e:
            logger.error(f"❌ [S3] Upload to AWS S3 FAILED: {e}", exc_info=True)
            return None


s3_service = S3Service()
