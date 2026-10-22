from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.donor import DonorProfile
from app.models.request import EmergencyRequest, RequestStatus

router = APIRouter(prefix="/stats", tags=["Dashboard Metrics"])


@router.get("/")
def get_system_stats(db: Session = Depends(get_db)):
    total_donors = db.query(DonorProfile).count()
    available_donors = db.query(DonorProfile).filter(DonorProfile.is_available == True).count()
    rare_donors = db.query(DonorProfile).filter(DonorProfile.is_rare_phenotype == True).count()

    total_requests = db.query(EmergencyRequest).count()
    active_requests = db.query(EmergencyRequest).filter(
        EmergencyRequest.status.in_([RequestStatus.OPEN, RequestStatus.DISPATCHED])
    ).count()
    fulfilled_requests = db.query(EmergencyRequest).filter(
        EmergencyRequest.status == RequestStatus.FULFILLED
    ).count()

    return {
        "total_registered_donors": total_donors,
        "currently_available_donors": available_donors,
        "rare_phenotype_donors": rare_donors,
        "total_emergency_broadcasts": total_requests,
        "active_emergency_alerts": active_requests,
        "transfusions_fulfilled": fulfilled_requests,
        "cloud_engine": "AWS Free Tier (EC2 t2.micro, RDS Postgres, S3, SNS, SES)",
        "server_status": "Healthy"
    }
