# 🩸 LifeLine - Cloud-Based Emergency Blood & Rare Donor Matching Network

A full-stack, enterprise-grade emergency blood dispatching and ultra-rare donor matching network optimized for AWS Free Tier without using Docker, built with React.js (Vite, Tailwind CSS, Lucide Icons), FastAPI (Python 3.11+), SQLAlchemy ORM, PostgreSQL (AWS RDS), Boto3 (AWS S3 SSE-S3 & SNS/SES), Nginx, and Systemd.

---

## 🌟 Key Features

### Emergency SOS Dispatch & Rare Phenotype Matching:
- **Ultra-Rare Phenotype Support**: Specialized matching algorithm for critical blood types including **Bombay ($O_h$)**, **Rh-null (Golden Blood)**, **Duffy Null $Fy(a-b-)$**, **Kell Null ($K_0$)**, and **Colton Null**.
- **Real-Time Automated Alerting**: Instant dispatch of transactional SMS notifications via **AWS SNS** and verified hospital emails via **AWS SES** when an emergency requisition is created.
- **Pledge & Fulfill Lifecycle**: Real-time transition of blood requisitions (`open` ➔ `matched` ➔ `fulfilled` / `cancelled`) with automated donor availability status management.
- **Proximity & Compatibility Engine**: Regional queries matching compatible donors based on ABO/Rh phenotypes, antigen profile notes, and municipal proximity.

### AWS Cloud Architecture & Direct Hosting (No Docker):
- **100% AWS Free Tier Optimized**: Runs on EC2 (`t2.micro` / `t3.micro`), RDS PostgreSQL (`db.t3.micro`), and S3 (5GB Free Tier) without paying for container services.
- **Native Systemd Daemon**: Automated daemon supervision via `lifeline.service` with memory sandboxing (`MemoryMax=650M`), auto-restart (`Restart=always`), and 2 tuned Uvicorn workers.
- **Nginx Reverse Proxy**: High-performance reverse proxy routing port 80/443 to the React SPA build (`/var/www/lifeline`) and proxying `/api` and `/docs` to FastAPI on port 8000 with Gzip compression.
- **2GB Swap Memory Allocator**: Integrated swap configuration (`setup_ec2.sh`) to eliminate Out-Of-Memory (OOM) failures on 1GB RAM Free Tier instances.

### Medical Document Vault & S3 Encryption:
- **Server-Side Encryption (SSE-S3 AES-256)**: All donor health fitness clearances and official hospital verification documents are automatically encrypted at rest using AES-256.
- **Pre-signed URL Security**: S3 bucket remains 100% private with all public access blocked. Authorized users view and upload documents strictly through short-lived presigned URLs (3600s expiration).
- **Client-to-S3 Direct Upload**: Browser sends documents directly to AWS S3 without overloading EC2 memory or backend threads.

### Role-Based Access Control & Portals:
- **Bcrypt & PyJWT Authorization**: Stateless Bearer token authentication safeguarding all protected API routes and donor records.
- **Four Distinct Roles**: Granular access control for **Patients**, **Donors**, **Hospitals**, and **Admins** enforced via `require_role()` dependency.
- **Interactive Role Dashboards**:
  - *Emergency SOS Portal*: Blood group selector badge grid in pale red cards, hospital picker, and urgency badges.
  - *Donor Management Dashboard*: Real-time availability toggle, document vault upload, and donation pledge history.
  - *Hospital Verification Center*: License upload and verification status management.
  - *Admin Analytics Center*: Live rare blood group distribution cards, emergency fulfillment rate %, and system telemetry.

### DevOps CI/CD & Automated Load Testing:
- **GitHub Actions Pipeline**: Automated CI/CD workflow testing backend integration, compiling frontend assets, and executing zero-downtime SSH deployments to AWS EC2 on push to `main`.
- **Locust Crisis Surge Load Testing**: Dedicated load testing suite (`locustfile.py`) simulating 100 to 1,000 concurrent users searching for rare blood and posting emergency requests with HTML/CSV reports.

---

## 📂 Project Structure

```
lifeline/
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Actions CI/CD automated SSH deployment pipeline
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings & AWS Free Tier configurations
│   │   │   ├── database.py         # SQLAlchemy engine with connection pool recycling
│   │   │   └── security.py         # Direct Bcrypt hashing, PyJWT tokens & require_role RBAC
│   │   ├── models/
│   │   │   ├── user.py             # User authentication model (UUID PK & UserRole enum)
│   │   │   ├── hospital.py         # Hospital profile & license verification model
│   │   │   ├── donor.py            # Donor profile with rare blood phenotypes & availability
│   │   │   ├── blood_request.py    # Emergency requisition model with urgency levels
│   │   │   └── donation.py         # Donation pledge & completion tracking model
│   │   ├── schemas/
│   │   │   ├── user.py             # User registration, login, and token schemas
│   │   │   ├── hospital.py         # Hospital profile & verification schemas
│   │   │   ├── donor.py            # Donor profile, search query, and availability schemas
│   │   │   ├── blood_request.py    # Emergency request creation and status update schemas
│   │   │   ├── donation.py         # Donation pledge and completion schemas
│   │   │   ├── document.py         # AWS S3 presigned URL request and response schemas
│   │   │   └── admin.py            # System analytics and rare blood telemetry schemas
│   │   ├── routers/
│   │   │   ├── auth.py             # POST /register, POST /login, GET /me
│   │   │   ├── hospitals.py        # GET / (verified hospitals), POST / (hospital registration)
│   │   │   ├── donors.py           # GET / (search by blood group & city), PUT /availability
│   │   │   ├── blood_requests.py   # POST / (create request & trigger SNS), GET /, PUT /{id}/status
│   │   │   ├── donations.py        # POST /pledge (donor pledge), PUT /{id}/complete
│   │   │   ├── documents.py        # POST /upload-url (Generate AWS S3 presigned upload URL)
│   │   │   └── admin.py            # GET /analytics (Match counts, rare blood stats, active donors)
│   │   ├── services/
│   │   │   ├── notifications.py    # AWS SNS (SMS) & SES (Email) emergency alert dispatcher
│   │   │   └── s3_service.py       # AWS S3 document uploader & presigned URL generator
│   │   └── main.py                 # FastAPI application, CORS, and database auto-seeding
│   ├── tests/
│   │   └── test_api.py             # Comprehensive test suite verifying all 7 API routers
│   ├── .env.example                # Documented environment variables template
│   └── requirements.txt            # Python dependencies (FastAPI, SQLAlchemy, PyJWT, Boto3)
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js           # Axios client with JWT Bearer token interceptor
│   │   ├── components/
│   │   │   ├── Navbar.jsx          # Pure white header with crimson accents & tab navigation
│   │   │   ├── AuthModal.jsx       # Role selector (Donor, Patient, Hospital, Admin) & auth
│   │   │   ├── EmergencySOSModal.jsx # SOS form with blood group badge selector grid
│   │   │   ├── LiveEmergencyFeed.jsx # Active requests feed with "Pledge to Donate" action
│   │   │   ├── DonorDirectory.jsx  # Search donors by blood group and city
│   │   │   ├── DonorPanel.jsx      # Donor dashboard: availability toggle & S3 upload
│   │   │   ├── HospitalPanel.jsx   # Hospital verification & license management
│   │   │   └── AdminAnalytics.jsx  # Rare blood group distribution & fulfillment telemetry
│   │   ├── App.jsx                 # Core SPA layout, toast alerts & session state
│   │   ├── main.jsx                # React DOM entry point
│   │   └── index.css               # Pale red background base layer & rose scrollbars
│   ├── index.html                  # Plus Jakarta Sans typography
│   ├── package.json                # Frontend dependencies (React 18, Axios, Lucide-react)
│   ├── vite.config.js              # Vite server & API proxy configuration
│   ├── tailwind.config.js          # Pale red / crimson rose aesthetic tokens
│   └── postcss.config.js           # PostCSS configuration
├── scripts/
│   ├── deploy.sh                   # Native deployment script (git pull, venv, build, restart)
│   ├── lifeline.service            # Systemd service unit file for EC2 Uvicorn daemon
│   ├── nginx.conf                  # Nginx reverse proxy & static SPA configuration
│   └── setup_ec2.sh                # Automated EC2 setup script (Nginx, Swap, Python venv, UFW)
├── docs/
│   └── aws_infrastructure_blueprint.md # Full guide for ALB, ASG, S3 SSE-S3, IAM & CloudWatch
├── locustfile.py                   # Locust load testing suite simulating 100-1000 concurrent users
├── .gitignore                      # Git ignore rules for node_modules, venv, and secrets
├── LICENSE                         # MIT License
└── README.md                       # Project documentation & reference manual
```

---

## 💻 Installation & Setup

### Prerequisites
- **Python**: v3.10+ (Python 3.11 or 3.12 recommended)
- **Node.js**: v18.0.0+ (with npm v9+)
- **Git**: Installed and configured on your system
- **PostgreSQL**: Local instance or AWS RDS PostgreSQL (`db.t3.micro` Free Tier)

---

### 1. Clone Repository
Ensure you are in your project directory:
```bash
git clone https://github.com/shyamsundarmd19-hub/Cloud-Emergency-Blood-Rare-Donor-Matching-Network.git
cd Cloud-Emergency-Blood-Rare-Donor-Matching-Network
```

---

### 2. Backend Setup & Virtual Environment
Navigate into the backend directory and set up the Python virtual environment:
```bash
cd backend
python -m venv venv

# Activate Virtual Environment:
# On Linux / macOS / AWS EC2:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Install backend dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 3. Database Setup
#### Option A: Automated SQLite / Auto-Seeding (Recommended for Development)
LifeLine includes an automated startup lifecycle that creates all relational tables and seeds initial demo data (admin, verified hospitals, rare blood donors, and active emergency requisitions) on startup.
Simply leave `DATABASE_URL` default in `.env`:
```bash
cp .env.example .env
```

#### Option B: AWS RDS PostgreSQL / Local PostgreSQL
For production or local PostgreSQL:
```bash
# Example PostgreSQL connection string
DATABASE_URL="postgresql://postgres:YourPassword@your-rds-endpoint.us-east-1.rds.amazonaws.com:5432/lifeline"
```

---

### 4. Configure Environment Variables
Create or verify the `.env` file in the `backend/` directory:
```env
PROJECT_NAME="LifeLine - Emergency Blood & Rare Donor Network"
ENVIRONMENT="production"
DEBUG=False
SECRET_KEY="replace-with-a-random-64-character-hex-string-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Database Connection (AWS RDS PostgreSQL or SQLite)
DATABASE_URL="sqlite:///./lifeline.db"

# AWS Region & S3 Vault Configuration
AWS_REGION="us-east-1"
AWS_S3_BUCKET_NAME="lifeline-medical-documents"
AWS_S3_SSE_ALGORITHM="AES256"
MAX_FILE_SIZE_MB=10

# AWS SNS / SES Notifications
AWS_SNS_TOPIC_ARN=""
SMS_SENDER_ID="LifeLine"
AWS_SES_SENDER_EMAIL="alerts@lifeline-emergency.org"

# AWS IAM Credentials (Optional if running on EC2 with IAM Instance Profile)
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
```

---

### 5. Frontend Build & Run

#### In Development Mode (with Live Reload):
```bash
# Terminal 1: Start FastAPI Backend Server
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Start React Frontend
cd frontend
npm install
npm run dev
```
Open your browser and visit: **[http://localhost:3000](http://localhost:3000)**

#### In Production Mode (Build Static Assets for Nginx):
```bash
cd frontend
npm install
npm run build
# Compiled files will be created in frontend/dist/ and served by Nginx from /var/www/lifeline
```

---

## 🌐 Live Demo & Endpoints

- **Repository URL**: [https://github.com/shyamsundarmd19-hub/Cloud-Emergency-Blood-Rare-Donor-Matching-Network.git](https://github.com/shyamsundarmd19-hub/Cloud-Emergency-Blood-Rare-Donor-Matching-Network.git)
- **Local Application Access**: [http://localhost:3000](http://localhost:3000)
- **Interactive Swagger API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc API Specifications**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **System Health Status Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🔑 Default Accounts & Sample Tracking Data (Created Automatically)

| Role / Entity | Identifier / Email | Default Password | Features Accessible |
| :--- | :--- | :--- | :--- |
| **Global Admin** | `admin@lifeline.org` | `AdminPass2026!` | Full Network Telemetry, Hospital Approvals, Admin Analytics, Rare Blood Distribution |
| **Rare Donor (Bombay $O_h$)** | `elena.vance@lifeline.org` | `DonorPass2026!` | Bombay Phenotype Profile, Availability Toggle, Health Clearance Upload, Pledges |
| **Rare Donor (Rh-null)** | `marcus.thorne@lifeline.org` | `DonorPass2026!` | Golden Blood Profile, Availability Toggle, S3 Clearance Vault, Pledges |
| **Universal Donor ($O^-$)** | `sarah.connor@lifeline.org` | `DonorPass2026!` | Universal Red Cell Profile, Regional Alert Feed, Availability Controls |
| **Hospital Authority** | `admin@stanfordhealth.org` | `HospitalPass2026!` | Verified Stanford Hospital Node, Emergency SOS Broadcast Creation, Complete Donation |
| **Hospital Authority** | `admin@mountsinai.org` | `HospitalPass2026!` | Mount Sinai Care Node, Clinical License Vault, Emergency Blood Requests |
| **Custom Registration** | Any valid email | User-defined (8+ chars) | Custom user registration with role selector (Donor, Patient, Hospital, Admin) |

---

## 🔒 Security Best Practices Implemented

1. **Server-Side Encryption at Rest (SSE-S3 AES-256)**: All medical records, doctor clearances, and hospital licenses uploaded to AWS S3 are encrypted at rest using AES-256 (`ServerSideEncryption='AES256'`).
2. **Private S3 Vault with Pre-signed URLs**: All 4 S3 Block Public Access controls are strictly enforced. Documents are accessed only via time-limited (3600s) presigned URLs generated on demand.
3. **Bcrypt Password Hashing**: Master user passwords are salted and hashed with bcrypt, ensuring cleartext credentials never touch persistent storage.
4. **JWT Role-Based Access Control (RBAC)**: All sensitive routes require valid Bearer token authorization, enforcing role checks (`donor`, `hospital`, `admin`, `patient`) via the `require_role()` dependency.
5. **Connection Pool Optimization for RDS**: SQLAlchemy engine pool is restricted to `pool_size=5` and `max_overflow=10` with `pool_recycle=1800` to prevent connection exhaustion on AWS RDS Free Tier instances (`db.t3.micro`).
6. **Systemd Security & Sandboxing**: Daemon configuration enforces `MemoryMax=650M`, `PrivateTmp=true`, and auto-restart to prevent Out-Of-Memory crashes and preserve operating system stability.
7. **Cross-Origin Resource Sharing (CORS)**: Strict origin whitelisting in production to prevent unauthorized cross-origin requests.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](file:///LICENSE) for more information.
