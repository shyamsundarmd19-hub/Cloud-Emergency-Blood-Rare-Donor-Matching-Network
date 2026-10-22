import logging
import os
import uuid
from typing import Optional, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import UploadFile
from app.core.config import settings

logger = logging.getLogger("lifeline.s3_service")

# Allowed MIME types for health and hospital verification documents
ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class S3Service:
    def __init__(self):
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        self.region = settings.AWS_REGION
        self._client = None

    def get_client(self):
        """Lazy-initialize boto3 S3 client using IAM role or configured credentials."""
        if self._client is None:
            kwargs = {"region_name": self.region}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

            try:
                self._client = boto3.client("s3", **kwargs)
            except Exception as e:
                logger.warning(f"Could not initialize Boto3 S3 client: {e}. Fallback mode active.")
                self._client = None
        return self._client

    async def upload_document(
        self,
        file: UploadFile,
        folder_prefix: str = "certificates",
        user_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Uploads file to AWS S3 using Server-Side Encryption (SSE-S3: AES256).
        Returns (success: bool, s3_key_or_error: str).
        """
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            return False, f"Invalid file format: {file.content_type}. Only PDF, JPG, and PNG are allowed."

        ext = ALLOWED_CONTENT_TYPES.get(file.content_type, ".pdf")
        unique_filename = f"{uuid.uuid4().hex[:12]}_{int(user_id or 0)}{ext}"
        s3_key = f"{folder_prefix}/{unique_filename}"

        client = self.get_client()

        # If AWS S3 credentials are not set (e.g. initial local dev), gracefully store in local uploads
        if not client:
            local_dir = os.path.join(os.getcwd(), "uploads", folder_prefix)
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, unique_filename)
            contents = await file.read()
            with open(local_path, "wb") as f:
                f.write(contents)
            logger.info(f"Local storage fallback used: {local_path}")
            return True, f"local://{s3_key}"

        try:
            file_bytes = await file.read()
            # Enforce Free Tier 10MB limit
            if len(file_bytes) > (settings.MAX_FILE_SIZE_MB * 1024 * 1024):
                return False, f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"

            client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_bytes,
                ContentType=file.content_type,
                ServerSideEncryption=settings.AWS_S3_SSE_ALGORITHM,  # SSE-S3 AES256
                Metadata={
                    "uploaded_by_user": str(user_id or "anonymous"),
                    "lifeline_module": folder_prefix,
                }
            )
            logger.info(f"Successfully uploaded {s3_key} to S3 bucket {self.bucket_name} with SSE-S3")
            return True, s3_key

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"S3 upload error: {e}")
            return False, f"Cloud storage upload error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            return False, str(e)

    def generate_presigned_url(self, s3_key: str, expires_in_seconds: int = 3600) -> Optional[str]:
        """
        Generate a secure pre-signed GET URL for authorized viewing of sensitive medical records.
        """
        if not s3_key:
            return None

        if s3_key.startswith("local://"):
            return f"/api/v1/documents/local/{s3_key.replace('local://', '')}"

        client = self.get_client()
        if not client:
            return None

        try:
            url = client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": s3_key,
                },
                ExpiresIn=expires_in_seconds,
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate pre-signed URL for {s3_key}: {e}")
            return None


s3_service = S3Service()
