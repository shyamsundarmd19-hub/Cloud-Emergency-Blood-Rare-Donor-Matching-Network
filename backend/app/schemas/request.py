from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.request import UrgencyLevel, RequestStatus


class EmergencyRequestBase(BaseModel):
    patient_name: str
    hospital_name: str
    blood_group: str
    units_needed: int = 1
    urgency: UrgencyLevel = UrgencyLevel.CRITICAL
    city: str
    state: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_phone: str
    medical_case_summary: Optional[str] = None


class EmergencyRequestCreate(EmergencyRequestBase):
    pass


class EmergencyRequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    units_needed: Optional[int] = None
    urgency: Optional[UrgencyLevel] = None
    medical_case_summary: Optional[str] = None


class EmergencyRequestResponse(EmergencyRequestBase):
    id: int
    requester_id: Optional[int] = None
    status: RequestStatus
    is_hospital_verified: bool
    hospital_verification_doc_s3_key: Optional[str] = None
    verification_doc_presigned_url: Optional[str] = None
    created_at: datetime
    fulfilled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmergencyDispatchResult(BaseModel):
    request_id: int
    matched_donors_count: int
    sms_notifications_sent: int
    email_alerts_sent: int
    status: str
