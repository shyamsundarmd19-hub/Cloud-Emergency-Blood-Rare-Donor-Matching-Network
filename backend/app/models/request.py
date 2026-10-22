import enum
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class UrgencyLevel(str, enum.Enum):
    CRITICAL = "critical"  # Immediate (Transfusion within < 2 hours)
    HIGH = "high"          # Urgent (Transfusion within 6 hours)
    STANDARD = "standard"  # Scheduled surgery / 24 hours


class RequestStatus(str, enum.Enum):
    OPEN = "open"
    DISPATCHED = "dispatched"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class EmergencyRequest(Base):
    __tablename__ = "emergency_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    patient_name = Column(String(255), nullable=False)
    hospital_name = Column(String(255), nullable=False, index=True)
    blood_group = Column(String(50), nullable=False, index=True)
    units_needed = Column(Integer, default=1, nullable=False)
    urgency = Column(Enum(UrgencyLevel), default=UrgencyLevel.CRITICAL, nullable=False, index=True)
    status = Column(Enum(RequestStatus), default=RequestStatus.OPEN, nullable=False, index=True)

    # Location of Hospital / Medical Centre
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Contact & Verification Details
    contact_phone = Column(String(30), nullable=False)
    medical_case_summary = Column(Text, nullable=True)

    # AWS S3 Document Storage (Hospital Requisition Form / Verification Document)
    hospital_verification_doc_s3_key = Column(String(500), nullable=True)
    is_hospital_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    fulfilled_at = Column(DateTime, nullable=True)

    # Relationships
    requester = relationship("User", back_populates="emergency_requests")
