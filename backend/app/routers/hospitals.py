from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.hospital import Hospital
from app.models.user import User, UserRole
from app.schemas.hospital import HospitalCreate, HospitalResponse

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])


@router.get("/", response_model=List[HospitalResponse])
def list_verified_hospitals(
    city: Optional[str] = Query(None, description="Filter by city name"),
    db: Session = Depends(get_db)
):
    """
    List all verified partner hospitals. Publicly accessible for transparency.
    """
    query = db.query(Hospital).filter(Hospital.is_verified == True)
    if city:
        query = query.filter(Hospital.city.ilike(f"%{city}%"))
    return query.all()


@router.post("/", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
def register_hospital(
    hospital_in: HospitalCreate,
    current_user: User = Depends(require_role("hospital", "admin")),
    db: Session = Depends(get_db)
):
    """
    Register a hospital profile linked to the authenticated hospital user account.
    Stores S3 document key for license verification.
    """
    existing_profile = db.query(Hospital).filter(Hospital.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A hospital profile already exists for this account."
        )

    duplicate_license = db.query(Hospital).filter(Hospital.license_number == hospital_in.license_number).first()
    if duplicate_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A hospital with this medical license number is already registered."
        )

    hospital = Hospital(
        user_id=current_user.id,
        hospital_name=hospital_in.hospital_name,
        license_number=hospital_in.license_number,
        city=hospital_in.city,
        address=hospital_in.address,
        verification_doc_url=hospital_in.verification_doc_url,
        is_verified=False  # Requires Admin verification
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


@router.patch("/{hospital_id}/verify", response_model=HospitalResponse)
def verify_hospital(
    hospital_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to approve a hospital license document stored in AWS S3.
    """
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")

    hospital.is_verified = True
    db.commit()
    db.refresh(hospital)
    return hospital
