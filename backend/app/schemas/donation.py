from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.donation import DonationStatus
from app.schemas.blood_request import BloodRequestResponse
from app.schemas.donor import DonorResponse


class DonationPledgeCreate(BaseModel):
    request_id: str


class DonationStatusUpdate(BaseModel):
    status: DonationStatus


class DonationResponse(BaseModel):
    id: str
    request_id: str
    donor_id: str
    status: DonationStatus
    donated_at: Optional[datetime] = None
    blood_request: Optional[BloodRequestResponse] = None
    donor: Optional[DonorResponse] = None

    class Config:
        from_attributes = True
