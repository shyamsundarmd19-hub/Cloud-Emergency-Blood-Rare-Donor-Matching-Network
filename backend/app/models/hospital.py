import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    hospital_name = Column(String(255), nullable=False, index=True)
    license_number = Column(String(100), unique=True, nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    address = Column(Text, nullable=False)
    verification_doc_url = Column(String(500), nullable=True)  # AWS S3 Key
    is_verified = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="hospital_profile")
    blood_requests = relationship("BloodRequest", back_populates="hospital", cascade="all, delete-orphan")
