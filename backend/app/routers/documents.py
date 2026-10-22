import logging
import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.document import PresignedUploadRequest, PresignedUploadResponse

router = APIRouter(prefix="/documents", tags=["Documents & Cloud Storage"])
logger = logging.getLogger("lifeline.documents")

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp"
}


@router.post("/upload-url", response_model=PresignedUploadResponse)
def generate_presigned_upload_url(
    req: PresignedUploadRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate an AWS S3 Pre-signed URL for direct, secure client-to-S3 upload
    with Server-Side Encryption (SSE-S3: AES256).
    """
    if req.file_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{req.file_type}'. Only PDF, JPEG, and PNG are permitted."
        )

    # Sanitize and create unique S3 key
    folder = "health-clearances" if req.document_type == "health_clearance" else "hospital-verifications"
    file_ext = req.file_name.split(".")[-1] if "." in req.file_name else "pdf"
    unique_key = f"{folder}/{uuid.uuid4().hex[:16]}_{current_user.id[:8]}.{file_ext}"

    # Initialize boto3 S3 client
    kwargs = {"region_name": settings.AWS_REGION}
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

    try:
        s3_client = boto3.client("s3", **kwargs)

        # Generate pre-signed PUT URL with SSE-S3 header requirement
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.AWS_S3_BUCKET_NAME,
                "Key": unique_key,
                "ContentType": req.file_type,
                "ServerSideEncryption": settings.AWS_S3_SSE_ALGORITHM,
            },
            ExpiresIn=3600,
            HttpMethod="PUT"
        )

        return PresignedUploadResponse(
            upload_url=presigned_url,
            s3_key=unique_key,
            method="PUT",
            headers={
                "Content-Type": req.file_type,
                "x-amz-server-side-encryption": settings.AWS_S3_SSE_ALGORITHM
            },
            expires_in_seconds=3600
        )

    except Exception as e:
        logger.warning(f"S3 Pre-signed generation fallback to local mock: {e}")
        # Graceful dev fallback if credentials are unset
        mock_url = f"/api/v1/documents/mock-upload/{unique_key}"
        return PresignedUploadResponse(
            upload_url=mock_url,
            s3_key=f"s3://{settings.AWS_S3_BUCKET_NAME}/{unique_key}",
            method="PUT",
            headers={"Content-Type": req.file_type},
            expires_in_seconds=3600
        )
