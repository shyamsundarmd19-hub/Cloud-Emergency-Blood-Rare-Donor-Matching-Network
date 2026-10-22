from datetime import date, datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.blood_request import BloodRequest, RequestStatus
from app.models.donation import Donation, DonationStatus
from app.models.donor import Donor
from app.models.user import User
from app.schemas.donation import DonationPledgeCreate, DonationResponse

router = APIRouter(prefix="/donations", tags=["Donations"])


@router.post("/pledge", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
def pledge_donation(
    pledge_in: DonationPledgeCreate,
    current_user: User = Depends(require_role("donor", "admin")),
    db: Session = Depends(get_db)
):
    """
    Authenticated donor pledges to donate blood for an active emergency blood request.
    Transitions request status to 'matched'.
    """
    # 1. Fetch donor profile
    donor = db.query(Donor).filter(Donor.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must complete your donor profile before pledging to donate."
        )

    # 2. Fetch blood request
    blood_request = db.query(BloodRequest).filter(BloodRequest.id == pledge_in.request_id).first()
    if not blood_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood request not found.")

    if blood_request.status in [RequestStatus.FULFILLED, RequestStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This blood request is already {blood_request.status.value}."
        )

    # 3. Check for existing active pledge by this donor
    existing_pledge = db.query(Donation).filter(
        Donation.request_id == pledge_in.request_id,
        Donation.donor_id == donor.id,
        Donation.status == DonationStatus.PLEDGED
    ).first()

    if existing_pledge:
        return existing_pledge

    # 4. Create Donation pledge
    donation = Donation(
        request_id=blood_request.id,
        donor_id=donor.id,
        status=DonationStatus.PLEDGED,
    )
    db.add(donation)

    # Update request status to MATCHED if currently OPEN
    if blood_request.status == RequestStatus.OPEN:
        blood_request.status = RequestStatus.MATCHED

    db.commit()
    db.refresh(donation)
    return donation


@router.put("/{donation_id}/complete", response_model=DonationResponse)
def complete_donation(
    donation_id: str,
    current_user: User = Depends(require_role("hospital", "admin")),
    db: Session = Depends(get_db)
):
    """
    Hospital or Admin confirms that blood donation was successfully completed.
    Updates donor's last_donated_date and marks donation as COMPLETED.
    """
    donation = db.query(Donation).join(BloodRequest).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation record not found.")

    donation.status = DonationStatus.COMPLETED
    donation.donated_at = datetime.now(timezone.utc)

    # Update donor record: last donated date & temporarily pause availability
    if donation.donor:
        donation.donor.last_donated_date = date.today()
        donation.donor.is_available = False

    # Check if request has collected required completed units
    req = donation.blood_request
    if req:
        completed_units = db.query(Donation).filter(
            Donation.request_id == req.id,
            Donation.status == DonationStatus.COMPLETED
        ).count()

        if completed_units >= req.units_required:
            req.status = RequestStatus.FULFILLED

    db.commit()
    db.refresh(donation)
    return donation


@router.get("/my-pledges", response_model=List[DonationResponse])
def get_my_pledges(
    current_user: User = Depends(require_role("donor", "admin")),
    db: Session = Depends(get_db)
):
    """
    Get all donation pledges made by the authenticated donor.
    """
    donor = db.query(Donor).filter(Donor.user_id == current_user.id).first()
    if not donor:
        return []

    return db.query(Donation).filter(Donation.donor_id == donor.id).all()
