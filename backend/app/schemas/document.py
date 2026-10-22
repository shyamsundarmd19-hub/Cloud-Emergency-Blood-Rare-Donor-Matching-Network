from typing import Optional
from pydantic import BaseModel


class PresignedUploadRequest(BaseModel):
    file_name: str
    file_type: str  # e.g. application/pdf, image/jpeg, image/png
    document_type: str  # "health_clearance" or "hospital_verification"


class PresignedUploadResponse(BaseModel):
    upload_url: str
    s3_key: str
    method: str = "PUT"
    headers: dict
    expires_in_seconds: int = 3600
