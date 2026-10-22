import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DONOR = "donor"
    HOSPITAL = "hospital"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(30), unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.DONOR, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    hospital_profile = relationship("Hospital", back_populates="user", uselist=False, cascade="all, delete-orphan")
    donor_profile = relationship("Donor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    blood_requests = relationship("BloodRequest", back_populates="requester", foreign_keys="BloodRequest.requester_id", cascade="all, delete-orphan")
