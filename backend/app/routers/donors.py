from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.donor import Donor
from app.models.user import User
from app.schemas.donor import DonorAvailabilityUpdate, DonorCreate, DonorResponse

router = APIRouter(prefix="/donors", tags=["Donors"])


@router.get("/", response_model=List[DonorResponse])
def search_donors(
    blood_group: Optional[str] = Query(None, description="Blood group e.g. 'O-', 'A+', 'Bombay (Oh)', 'Rh-null'"),
    city: Optional[str] = Query(None, description="City name"),
    available_only: bool = Query(True, description="Filter for active donors ready to donate"),
    db: Session = Depends(get_db)
):
    """
    Search available donors by blood group and city.
    """
    query = db.query(Donor)

    if available_only:
        query = query.filter(Donor.is_available == True)

    if blood_group:
        query = query.filter(Donor.blood_group.ilike(f"%{blood_group}%"))

    if city:
        query = query.filter(Donor.city.ilike(f"%{city}%"))

    return query.limit(100).all()


@router.post("/", response_model=DonorResponse, status_code=status.HTTP_201_CREATED)
def register_donor_profile(
    donor_in: DonorCreate,
    current_user: User = Depends(require_role("donor", "admin")),
    db: Session = Depends(get_db)
):
    """
    Register or link a donor profile with blood group, age, city, and S3 clearance certificate.
    """
    existing_profile = db.query(Donor).filter(Donor.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A donor profile is already registered for this user account."
        )

    donor = Donor(
        user_id=current_user.id,
        blood_group=donor_in.blood_group,
        age=donor_in.age,
        gender=donor_in.gender,
        city=donor_in.city,
        last_donated_date=donor_in.last_donated_date,
        health_clearance_url=donor_in.health_clearance_url,
        is_available=donor_in.is_available,
    )
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor


@router.put("/availability", response_model=DonorResponse)
def toggle_donor_availability(
    availability_in: DonorAvailabilityUpdate,
    current_user: User = Depends(require_role("donor", "admin")),
    db: Session = Depends(get_db)
):
    """
    Toggle donor availability status between available and paused.
    """
    donor = db.query(Donor).filter(Donor.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found for the current user."
        )

    donor.is_available = availability_in.is_available
    db.commit()
    db.refresh(donor)
    return donor
