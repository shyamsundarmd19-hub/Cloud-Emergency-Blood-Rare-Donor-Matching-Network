import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class DonationStatus(str, enum.Enum):
    PLEDGED = "pledged"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Donation(Base):
    __tablename__ = "donations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    request_id = Column(String(36), ForeignKey("blood_requests.id", ondelete="CASCADE"), nullable=False)
    donor_id = Column(String(36), ForeignKey("donors.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(DonationStatus), default=DonationStatus.PLEDGED, nullable=False, index=True)
    donated_at = Column(DateTime, nullable=True)

    # Relationships
    blood_request = relationship("BloodRequest", back_populates="donations")
    donor = relationship("Donor", back_populates="donations")
