from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.donor import DonorProfile
from app.models.request import EmergencyRequest, RequestStatus, UrgencyLevel
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.request import (
    EmergencyDispatchResult,
    EmergencyRequestCreate,
    EmergencyRequestResponse,
    EmergencyRequestUpdate,
)
from app.services.notification_service import notification_service
from app.services.s3_service import s3_service

router = APIRouter(prefix="/requests", tags=["Emergency Requests"])


@router.post("/", response_model=EmergencyRequestResponse, status_code=status.HTTP_201_CREATED)
def create_emergency_request(
    request_in: EmergencyRequestCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_request = EmergencyRequest(
        requester_id=current_user.id if current_user else None,
        patient_name=request_in.patient_name,
        hospital_name=request_in.hospital_name,
        blood_group=request_in.blood_group,
        units_needed=request_in.units_needed,
        urgency=request_in.urgency,
        city=request_in.city,
        state=request_in.state,
        latitude=request_in.latitude,
        longitude=request_in.longitude,
        contact_phone=request_in.contact_phone,
        medical_case_summary=request_in.medical_case_summary,
        status=RequestStatus.OPEN,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


@router.post("/{request_id}/upload-verification")
async def upload_hospital_verification(
    request_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload official hospital requisition form / doctor memo to AWS S3 with SSE-S3.
    """
    req = db.query(EmergencyRequest).filter(EmergencyRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency request not found.")

    success, result = await s3_service.upload_document(
        file=file,
        folder_prefix="hospital-verifications",
        user_id=req.requester_id
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result)

    req.hospital_verification_doc_s3_key = result
    req.is_hospital_verified = True
    db.commit()
    db.refresh(req)

    return {
        "message": "Hospital verification document saved to S3.",
        "s3_key": result,
        "is_hospital_verified": True
    }


@router.post("/{request_id}/dispatch", response_model=EmergencyDispatchResult)
async def dispatch_emergency_alert(request_id: int, db: Session = Depends(get_db)):
    """
    High-priority matching engine: Finds compatible available donors in the vicinity
    and fires real-time SMS alerts via AWS SNS + Regional Hospital alerts via AWS SES.
    """
    req = db.query(EmergencyRequest).filter(EmergencyRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")

    # Match donors with requested blood group, available, same city/region
    matching_donors = db.query(DonorProfile).join(User).filter(
        DonorProfile.blood_group == req.blood_group,
        DonorProfile.is_available == True,
        DonorProfile.city.ilike(f"%{req.city}%")
    ).all()

    sms_count = 0
    email_count = 0

    sms_message = (
        f"[URGENT LifeLine Alert] Blood Group {req.blood_group} desperately needed for patient "
        f"at {req.hospital_name}, {req.city}! Contact: {req.contact_phone}. Urgency: {req.urgency.value.upper()}."
    )

    # 1. Dispatch SMS alerts to matched donors via AWS SNS
    for donor in matching_donors:
        if donor.user and donor.user.phone_number:
            sent = await notification_service.send_emergency_sms(
                phone_number=donor.user.phone_number,
                message=sms_message
            )
            if sent:
                sms_count += 1

    # 2. Dispatch Regional Email Alert via AWS SES
    email_html = f"""
    <div style="font-family: Arial, sans-serif; background-color: #fffaf0; padding: 24px; border-radius: 8px;">
        <h2 style="color: #ea580c;">🚨 LifeLine Emergency Blood Dispatch Notification</h2>
        <p>An emergency transfusion request has been broadcasted:</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
            <tr><td style="padding: 8px; font-weight: bold; color: #7c2d12;">Patient / Case:</td><td style="padding: 8px;">{req.patient_name}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #7c2d12;">Hospital:</td><td style="padding: 8px;">{req.hospital_name} ({req.city}, {req.state})</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #7c2d12;">Blood Type:</td><td style="padding: 8px; font-size: 1.25rem; font-weight: bold; color: #ea580c;">{req.blood_group}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #7c2d12;">Units Needed:</td><td style="padding: 8px;">{req.units_needed} unit(s)</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #7c2d12;">Urgency Level:</td><td style="padding: 8px; text-transform: uppercase; font-weight: bold;">{req.urgency.value}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #7c2d12;">Contact Hotline:</td><td style="padding: 8px;">{req.contact_phone}</td></tr>
        </table>
        <p style="color: #9a3412; font-size: 0.875rem;">Dispatched by LifeLine Cloud Node on AWS Free Tier.</p>
    </div>
    """

    email_recipients = [donor.user.email for donor in matching_donors if donor.user and donor.user.email]
    if email_recipients:
        email_sent = await notification_service.send_emergency_email(
            recipient_emails=email_recipients,
            subject=f"[CRITICAL BLOOD NEED] {req.blood_group} required at {req.hospital_name}",
            body_html=email_html
        )
        if email_sent:
            email_count = len(email_recipients)

    # Update request status
    req.status = RequestStatus.DISPATCHED
    db.commit()

    return EmergencyDispatchResult(
        request_id=req.id,
        matched_donors_count=len(matching_donors),
        sms_notifications_sent=sms_count,
        email_alerts_sent=email_count,
        status="Dispatched"
    )


@router.get("/", response_model=List[EmergencyRequestResponse])
def list_emergency_requests(
    status: Optional[RequestStatus] = None,
    city: Optional[str] = None,
    blood_group: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(EmergencyRequest)

    if status:
        query = query.filter(EmergencyRequest.status == status)
    if city:
        query = query.filter(EmergencyRequest.city.ilike(f"%{city}%"))
    if blood_group:
        query = query.filter(EmergencyRequest.blood_group == blood_group)

    requests = query.order_by(EmergencyRequest.created_at.desc()).limit(limit).all()

    for item in requests:
        if item.hospital_verification_doc_s3_key:
            item.verification_doc_presigned_url = s3_service.generate_presigned_url(
                item.hospital_verification_doc_s3_key, expires_in_seconds=1800
            )

    return requests


@router.patch("/{request_id}", response_model=EmergencyRequestResponse)
def update_request_status(
    request_id: int,
    update_in: EmergencyRequestUpdate,
    db: Session = Depends(get_db)
):
    req = db.query(EmergencyRequest).filter(EmergencyRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")

    if update_in.status:
        req.status = update_in.status
        if update_in.status == RequestStatus.FULFILLED:
            req.fulfilled_at = datetime.now(timezone.utc)
    if update_in.units_needed is not None:
        req.units_needed = update_in.units_needed
    if update_in.urgency:
        req.urgency = update_in.urgency
    if update_in.medical_case_summary:
        req.medical_case_summary = update_in.medical_case_summary

    db.commit()
    db.refresh(req)
    return req
