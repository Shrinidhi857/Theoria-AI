import os
import sys
import logging
from dotenv import load_dotenv

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from app.core.config import settings
from app.services.s3_service import S3Service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_s3_upload():
    """
    Creates a small test file and uploads it to AWS S3 using configured credentials.
    """
    logger.info("Initializing S3Service...")
    s3 = S3Service()

    logger.info(f"S3 Configured: {s3.is_configured}")
    logger.info(f"Bucket Name: '{settings.AWS_S3_BUCKET}'")
    logger.info(f"AWS Region: '{settings.AWS_REGION}'")
    logger.info(f"Custom Domain: '{settings.AWS_S3_CUSTOM_DOMAIN or '(None - Using default S3 URL)'}'")

    if not s3.is_configured:
        logger.error("❌ AWS S3 credentials missing in .env configuration.")
        return

    # Create dummy test file
    test_file_path = os.path.abspath("s3_test_file.mp4")
    with open(test_file_path, "wb") as f:
        f.write(b"Theoria AI AWS S3 Upload Test File Content\n")

    try:
        logger.info(f"Testing upload of local file '{test_file_path}' to S3...")
        s3_url = s3.upload_video(test_file_path, s3_key="test/s3_test_file.mp4")
        if s3_url:
            logger.info(f"🎉 SUCCESS! S3 File Upload Succeeded!")
            logger.info(f"Public URL: {s3_url}")
        else:
            logger.error("❌ S3 Upload failed or returned None.")
    finally:
        # Clean up local dummy file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


if __name__ == "__main__":
    test_s3_upload()
