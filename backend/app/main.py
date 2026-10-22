from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models.blood_request import BloodRequest, RequestStatus, UrgencyLevel
from app.models.donation import Donation, DonationStatus
from app.models.donor import Donor
from app.models.hospital import Hospital
from app.models.user import User, UserRole
from app.routers import admin, auth, blood_requests, documents, donations, donors, hospitals


def seed_database_demo_records():
    """Seeds rich sample data for hospitals, rare donors, emergency requests, and pledges."""
    db = SessionLocal()
    try:
        # Check if users already seeded
        if db.query(User).count() > 0:
            return

        # 1. Admin User
        admin_user = User(
            name="LifeLine Global Admin",
            email="admin@lifeline.org",
            phone="+18005550100",
            role=UserRole.ADMIN,
            password_hash=get_password_hash("AdminPass2026!"),
        )
        db.add(admin_user)
        db.flush()

        # 2. Hospital Accounts & Profiles
        hosp_user_1 = User(
            name="Stanford Health Admin",
            email="admin@stanfordhealth.org",
            phone="+16507234000",
            role=UserRole.HOSPITAL,
            password_hash=get_password_hash("HospitalPass2026!"),
        )
        hosp_user_2 = User(
            name="Mount Sinai Care Admin",
            email="admin@mountsinai.org",
            phone="+12122416500",
            role=UserRole.HOSPITAL,
            password_hash=get_password_hash("HospitalPass2026!"),
        )
        db.add_all([hosp_user_1, hosp_user_2])
        db.flush()

        hospital_1 = Hospital(
            user_id=hosp_user_1.id,
            hospital_name="Stanford Hospital & Trauma Center",
            license_number="CA-MED-994821",
            city="Palo Alto",
            address="300 Pasteur Dr, Palo Alto, CA 94304",
            verification_doc_url="hospital-verifications/stanford_license.pdf",
            is_verified=True,
        )
        hospital_2 = Hospital(
            user_id=hosp_user_2.id,
            hospital_name="Mount Sinai Medical Center",
            license_number="NY-HOSP-551209",
            city="New York",
            address="1468 Madison Ave, New York, NY 10029",
            verification_doc_url="hospital-verifications/mount_sinai_license.pdf",
            is_verified=True,
        )
        db.add_all([hospital_1, hospital_2])
        db.flush()

        # 3. Patient User
        patient_user = User(
            name="Arthur Pendelton",
            email="arthur.pendelton@gmail.com",
            phone="+14155558899",
            role=UserRole.PATIENT,
            password_hash=get_password_hash("PatientPass2026!"),
        )
        db.add(patient_user)
        db.flush()

        # 4. Donors with Common & Ultra-Rare Blood Phenotypes
        donor_configs = [
            {
                "name": "Dr. Elena Vance",
                "email": "elena.vance@lifeline.org",
                "phone": "+14155552671",
                "blood_group": "Bombay (Oh)",
                "age": 32,
                "gender": "Female",
                "city": "Palo Alto",
                "available": True,
                "last_donated": date(2026, 4, 15),
            },
            {
                "name": "Marcus Aurelius Thorne",
                "email": "marcus.thorne@lifeline.org",
                "phone": "+12125559812",
                "blood_group": "Rh-null",
                "age": 38,
                "gender": "Male",
                "city": "New York",
                "available": True,
                "last_donated": date(2026, 1, 10),
            },
            {
                "name": "Sarah Connor",
                "email": "sarah.connor@lifeline.org",
                "phone": "+13125553311",
                "blood_group": "O-",
                "age": 29,
                "gender": "Female",
                "city": "Chicago",
                "available": True,
                "last_donated": date(2026, 6, 20),
            },
            {
                "name": "Rajesh Sharma",
                "email": "rajesh.sharma@lifeline.org",
                "phone": "+15125558900",
                "blood_group": "Kell Null (K0)",
                "age": 41,
                "gender": "Male",
                "city": "Austin",
                "available": True,
                "last_donated": None,
            },
            {
                "name": "Clara Oswald",
                "email": "clara.oswald@lifeline.org",
                "phone": "+12065554422",
                "blood_group": "Duffy Null Fy(a-b-)",
                "age": 27,
                "gender": "Female",
                "city": "Palo Alto",
                "available": True,
                "last_donated": date(2026, 3, 5),
            },
            {
                "name": "David Kim",
                "email": "david.kim@lifeline.org",
                "phone": "+16175557788",
                "blood_group": "B+",
                "age": 34,
                "gender": "Male",
                "city": "Boston",
                "available": True,
                "last_donated": date(2026, 7, 1),
            }
        ]

        seeded_donors = []
        for d in donor_configs:
            u = User(
                name=d["name"],
                email=d["email"],
                phone=d["phone"],
                role=UserRole.DONOR,
                password_hash=get_password_hash("DonorPass2026!"),
            )
            db.add(u)
            db.flush()

            donor_prof = Donor(
                user_id=u.id,
                blood_group=d["blood_group"],
                age=d["age"],
                gender=d["gender"],
                city=d["city"],
                last_donated_date=d["last_donated"],
                health_clearance_url="health-clearances/cert_verified.pdf",
                is_available=d["available"]
            )
            db.add(donor_prof)
            seeded_donors.append(donor_prof)

        db.flush()

        # 5. Urgent Emergency Blood Requests
        req_1 = BloodRequest(
            requester_id=patient_user.id,
            hospital_id=hospital_1.id,
            patient_name="Baby Maya Lin (Neonatal ICU)",
            blood_group="Bombay (Oh)",
            units_required=2,
            urgency_level=UrgencyLevel.CRITICAL,
            status=RequestStatus.MATCHED,
        )
        req_2 = BloodRequest(
            requester_id=hosp_user_2.id,
            hospital_id=hospital_2.id,
            patient_name="James Wilson (Cardiothoracic Trauma)",
            blood_group="Rh-null",
            units_required=1,
            urgency_level=UrgencyLevel.CRITICAL,
            status=RequestStatus.OPEN,
        )
        req_3 = BloodRequest(
            requester_id=patient_user.id,
            hospital_id=hospital_1.id,
            patient_name="Clara Jenkins (Emergency Obstetrics)",
            blood_group="O-",
            units_required=3,
            urgency_level=UrgencyLevel.HIGH,
            status=RequestStatus.OPEN,
        )
        db.add_all([req_1, req_2, req_3])
        db.flush()

        # 6. Donation Pledge
        pledge_1 = Donation(
            request_id=req_1.id,
            donor_id=seeded_donors[0].id,  # Dr. Elena Vance (Bombay Oh)
            status=DonationStatus.PLEDGED,
        )
        db.add(pledge_1)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB Schema and Seed Sample Data
    Base.metadata.create_all(bind=engine)
    seed_database_demo_records()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Complete Core Backend & Emergency Blood Matching Database Layer for LifeLine.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory for local development mock uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include Core API Routers under /api/v1
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(hospitals.router, prefix=settings.API_V1_STR)
app.include_router(donors.router, prefix=settings.API_V1_STR)
app.include_router(blood_requests.router, prefix=settings.API_V1_STR)
app.include_router(donations.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)


@app.get("/api/health", tags=["Health"])
@app.get("/healthz", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "lifeline-backend",
        "version": settings.VERSION,
        "database": "connected"
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.PROJECT_NAME,
        "docs": "/docs",
        "version": settings.VERSION,
        "api_v1": settings.API_V1_STR,
        "routers": [
            f"{settings.API_V1_STR}/auth",
            f"{settings.API_V1_STR}/hospitals",
            f"{settings.API_V1_STR}/donors",
            f"{settings.API_V1_STR}/blood-requests",
            f"{settings.API_V1_STR}/donations",
            f"{settings.API_V1_STR}/documents",
            f"{settings.API_V1_STR}/admin"
        ]
    }
