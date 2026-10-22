from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UserResponse


class HospitalBase(BaseModel):
    hospital_name: str
    license_number: str
    city: str
    address: str
    verification_doc_url: Optional[str] = None


class HospitalCreate(HospitalBase):
    pass


class HospitalResponse(HospitalBase):
    id: str
    user_id: str
    is_verified: bool
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True
