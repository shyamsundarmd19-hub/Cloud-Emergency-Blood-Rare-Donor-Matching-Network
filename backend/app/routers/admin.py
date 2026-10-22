from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.models.blood_request import BloodRequest, RequestStatus
from app.models.donation import Donation, DonationStatus
from app.models.donor import Donor
from app.models.hospital import Hospital
from app.models.user import User
from app.schemas.admin import AnalyticsResponse

router = APIRouter(prefix="/admin", tags=["Admin & Analytics"])

RARE_BLOOD_TYPES = [
    "Bombay (Oh)",
    "Rh-null",
    "Duffy Null Fy(a-b-)",
    "Kell Null (K0)",
    "Colton Null Co(a-b-)",
    "Lutheran Null Lu(a-b-)",
    "Vel-Negative"
]


@router.get("/analytics", response_model=AnalyticsResponse)
def get_admin_analytics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Fetch comprehensive administrative analytics:
    - Emergency match count
    - Active donor count
    - Rare blood group statistics
    - Hospital, request, and donation metrics
    """
    total_donors = db.query(Donor).count()
    active_donors = db.query(Donor).filter(Donor.is_available == True).count()
    verified_hospitals = db.query(Hospital).filter(Hospital.is_verified == True).count()

    total_requests = db.query(BloodRequest).count()
    matched_requests = db.query(BloodRequest).filter(
        BloodRequest.status.in_([RequestStatus.MATCHED, RequestStatus.FULFILLED])
    ).count()
    fulfilled_requests = db.query(BloodRequest).filter(BloodRequest.status == RequestStatus.FULFILLED).count()

    completed_donations = db.query(Donation).filter(Donation.status == DonationStatus.COMPLETED).count()
    pledged_donations = db.query(Donation).filter(Donation.status == DonationStatus.PLEDGED).count()

    # Aggregate distribution of all blood groups
    blood_distribution_rows = db.query(
        Donor.blood_group, func.count(Donor.id)
    ).group_by(Donor.blood_group).all()
    blood_group_distribution: Dict[str, int] = {bg: count for bg, count in blood_distribution_rows}

    # Aggregate specifically rare blood phenotypes
    rare_stats: Dict[str, int] = {}
    for rare_bg in RARE_BLOOD_TYPES:
        count = db.query(Donor).filter(Donor.blood_group.ilike(f"%{rare_bg}%")).count()
        if count > 0:
            rare_stats[rare_bg] = count

    return AnalyticsResponse(
        emergency_match_count=matched_requests,
        active_donor_count=active_donors,
        total_donor_count=total_donors,
        verified_hospital_count=verified_hospitals,
        total_blood_requests=total_requests,
        fulfilled_blood_requests=fulfilled_requests,
        completed_donations=completed_donations,
        pledged_donations=pledged_donations,
        rare_blood_group_statistics=rare_stats,
        blood_group_distribution=blood_group_distribution
    )
