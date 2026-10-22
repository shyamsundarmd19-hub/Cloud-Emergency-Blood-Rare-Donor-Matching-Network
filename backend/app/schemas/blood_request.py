from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.blood_request import RequestStatus, UrgencyLevel
from app.schemas.hospital import HospitalResponse
from app.schemas.user import UserResponse


class BloodRequestBase(BaseModel):
    hospital_id: str
    patient_name: str
    blood_group: str
    units_required: int = 1
    urgency_level: UrgencyLevel = UrgencyLevel.CRITICAL


class BloodRequestCreate(BloodRequestBase):
    pass


class BloodRequestStatusUpdate(BaseModel):
    status: RequestStatus


class BloodRequestResponse(BloodRequestBase):
    id: str
    requester_id: Optional[str] = None
    status: RequestStatus
    created_at: datetime
    hospital: Optional[HospitalResponse] = None
    requester: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class BloodRequestCreateResponse(BaseModel):
    blood_request: BloodRequestResponse
    notification_summary: dict
