from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.blood_request import BloodRequest, RequestStatus
from app.models.donor import Donor
from app.models.hospital import Hospital
from app.models.user import User
from app.schemas.blood_request import (
    BloodRequestCreate,
    BloodRequestCreateResponse,
    BloodRequestResponse,
    BloodRequestStatusUpdate,
)
from app.services.notifications import notification_service

router = APIRouter(prefix="/blood-requests", tags=["Blood Requests"])


@router.post("/", response_model=BloodRequestCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_blood_request(
    request_in: BloodRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create an emergency blood request and automatically trigger instant AWS SNS/SES alerts
    to all active compatible donors in the regional area.
    """
    # Verify hospital exists
    hospital = db.query(Hospital).filter(Hospital.id == request_in.hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found with the provided hospital_id."
        )

    # 1. Create the BloodRequest record
    db_request = BloodRequest(
        requester_id=current_user.id,
        hospital_id=request_in.hospital_id,
        patient_name=request_in.patient_name,
        blood_group=request_in.blood_group,
        units_required=request_in.units_required,
        urgency_level=request_in.urgency_level,
        status=RequestStatus.OPEN,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # 2. Query matching active donors in the hospital's vicinity
    matching_donors = db.query(Donor).join(User).filter(
        Donor.blood_group.ilike(f"%{db_request.blood_group}%"),
        Donor.is_available == True,
        Donor.city.ilike(f"%{hospital.city}%")
    ).all()

    # Fallback to wider regional match if none found in exact city
    if not matching_donors:
        matching_donors = db.query(Donor).join(User).filter(
            Donor.blood_group.ilike(f"%{db_request.blood_group}%"),
            Donor.is_available == True
        ).limit(20).all()

    donor_phones = [d.user.phone for d in matching_donors if d.user and d.user.phone]
    donor_emails = [d.user.email for d in matching_donors if d.user and d.user.email]

    # 3. Dispatch AWS SNS (SMS) & SES (Email) alerts
    alert_summary = await notification_service.trigger_critical_blood_alert(
        donor_phones=donor_phones,
        donor_emails=donor_emails,
        blood_group=db_request.blood_group,
        hospital_name=hospital.hospital_name,
        city=hospital.city,
        units_required=db_request.units_required,
        urgency=db_request.urgency_level.value,
        patient_name=db_request.patient_name
    )

    return BloodRequestCreateResponse(
        blood_request=db_request,
        notification_summary=alert_summary
    )


@router.get("/", response_model=List[BloodRequestResponse])
def list_blood_requests(
    status_filter: Optional[RequestStatus] = Query(None, alias="status", description="Filter by status (open, matched, fulfilled, cancelled)"),
    blood_group: Optional[str] = Query(None, description="Filter by blood group"),
    city: Optional[str] = Query(None, description="Filter by hospital city"),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """
    List emergency blood requests. Defaults to open requests when not specified.
    """
    query = db.query(BloodRequest).join(Hospital)

    if status_filter:
        query = query.filter(BloodRequest.status == status_filter)
    else:
        # By default, prioritize open and matched active emergencies
        query = query.filter(BloodRequest.status.in_([RequestStatus.OPEN, RequestStatus.MATCHED]))

    if blood_group:
        query = query.filter(BloodRequest.blood_group.ilike(f"%{blood_group}%"))

    if city:
        query = query.filter(Hospital.city.ilike(f"%{city}%"))

    return query.order_by(BloodRequest.created_at.desc()).limit(limit).all()


@router.put("/{request_id}/status", response_model=BloodRequestResponse)
def update_blood_request_status(
    request_id: str,
    status_in: BloodRequestStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update blood request lifecycle status (open -> matched -> fulfilled / cancelled).
    Requires the requester, associated hospital, or an admin.
    """
    blood_request = db.query(BloodRequest).filter(BloodRequest.id == request_id).first()
    if not blood_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood request not found.")

    # Authorization check
    is_admin = current_user.role == "admin" or getattr(current_user.role, "value", "") == "admin"
    is_requester = blood_request.requester_id == current_user.id
    is_hospital_owner = blood_request.hospital and blood_request.hospital.user_id == current_user.id

    if not (is_admin or is_requester or is_hospital_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this blood request."
        )

    blood_request.status = status_in.status
    db.commit()
    db.refresh(blood_request)
    return blood_request
