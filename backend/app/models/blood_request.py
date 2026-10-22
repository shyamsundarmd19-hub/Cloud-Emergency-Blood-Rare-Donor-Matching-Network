import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class UrgencyLevel(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"


class RequestStatus(str, enum.Enum):
    OPEN = "open"
    MATCHED = "matched"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    requester_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    hospital_id = Column(String(36), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)

    patient_name = Column(String(255), nullable=False)
    blood_group = Column(String(50), nullable=False, index=True)
    units_required = Column(Integer, default=1, nullable=False)
    urgency_level = Column(Enum(UrgencyLevel), default=UrgencyLevel.CRITICAL, nullable=False, index=True)
    status = Column(Enum(RequestStatus), default=RequestStatus.OPEN, nullable=False, index=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    requester = relationship("User", back_populates="blood_requests", foreign_keys=[requester_id])
    hospital = relationship("Hospital", back_populates="blood_requests")
    donations = relationship("Donation", back_populates="blood_request", cascade="all, delete-orphan")
