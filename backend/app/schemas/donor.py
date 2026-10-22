from datetime import date
from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UserResponse


class DonorBase(BaseModel):
    blood_group: str
    age: int
    gender: str
    city: str
    last_donated_date: Optional[date] = None
    health_clearance_url: Optional[str] = None
    is_available: bool = True


class DonorCreate(DonorBase):
    pass


class DonorAvailabilityUpdate(BaseModel):
    is_available: bool


class DonorResponse(DonorBase):
    id: str
    user_id: str
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True
