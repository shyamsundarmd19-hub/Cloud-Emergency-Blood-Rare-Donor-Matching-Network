import uuid
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Donor(Base):
    __tablename__ = "donors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    blood_group = Column(String(50), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    last_donated_date = Column(Date, nullable=True)
    health_clearance_url = Column(String(500), nullable=True)  # AWS S3 Key
    is_available = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="donor_profile")
    donations = relationship("Donation", back_populates="donor", cascade="all, delete-orphan")
