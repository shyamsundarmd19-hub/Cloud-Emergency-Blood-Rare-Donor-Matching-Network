import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app


def test_full_pipeline():
    with TestClient(app) as client:
        # 1. Health Check
        res = client.get("/api/health")
        assert res.status_code == 200, res.text
        assert res.json()["status"] == "healthy"

        # 2. Authentication (Admin, Donor, Hospital)
        admin_login = client.post("/api/v1/auth/login", json={
            "email": "admin@lifeline.org",
            "password": "AdminPass2026!"
        })
        assert admin_login.status_code == 200, admin_login.text
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        donor_login = client.post("/api/v1/auth/login", json={
            "email": "elena.vance@lifeline.org",
            "password": "DonorPass2026!"
        })
        assert donor_login.status_code == 200, donor_login.text
        donor_token = donor_login.json()["access_token"]
        donor_headers = {"Authorization": f"Bearer {donor_token}"}

        hosp_login = client.post("/api/v1/auth/login", json={
            "email": "admin@stanfordhealth.org",
            "password": "HospitalPass2026!"
        })
        assert hosp_login.status_code == 200, hosp_login.text
        hosp_token = hosp_login.json()["access_token"]
        hosp_headers = {"Authorization": f"Bearer {hosp_token}"}

        # 3. Hospitals
        hosp_res = client.get("/api/v1/hospitals/")
        assert hosp_res.status_code == 200
        hospitals = hosp_res.json()
        assert len(hospitals) >= 2
        stanford_id = hospitals[0]["id"]

        # 4. Donor Search & Availability Toggle
        bombay_search = client.get("/api/v1/donors/?blood_group=Bombay&available_only=false")
        assert bombay_search.status_code == 200
        assert len(bombay_search.json()) >= 1

        avail_res = client.put("/api/v1/donors/availability", headers=donor_headers, json={"is_available": True})
        assert avail_res.status_code == 200

        # 5. Blood Requests & SNS/SES Alerting
        req_payload = {
            "hospital_id": stanford_id,
            "patient_name": "Emergency Trauma Room 3",
            "blood_group": "Bombay (Oh)",
            "units_required": 1,
            "urgency_level": "critical"
        }
        create_req_res = client.post("/api/v1/blood-requests/", headers=hosp_headers, json=req_payload)
        assert create_req_res.status_code == 201
        created_req = create_req_res.json()
        req_id = created_req["blood_request"]["id"]
        assert created_req["notification_summary"]["matched_recipients"] >= 1

        # 6. Donations (Pledge & Complete)
        pledge_res = client.post("/api/v1/donations/pledge", headers=donor_headers, json={"request_id": req_id})
        assert pledge_res.status_code == 201
        donation_id = pledge_res.json()["id"]

        complete_res = client.put(f"/api/v1/donations/{donation_id}/complete", headers=hosp_headers)
        assert complete_res.status_code == 200
        assert complete_res.json()["status"] == "completed"

        # 7. S3 Presigned URL Generation
        doc_res = client.post("/api/v1/documents/upload-url", headers=donor_headers, json={
            "file_name": "donor_health_clearance.pdf",
            "file_type": "application/pdf",
            "document_type": "health_clearance"
        })
        assert doc_res.status_code == 200
        assert "upload_url" in doc_res.json()
        assert "s3_key" in doc_res.json()

        # 8. Admin Analytics
        admin_res = client.get("/api/v1/admin/analytics", headers=admin_headers)
        assert admin_res.status_code == 200
        analytics = admin_res.json()
        assert analytics["active_donor_count"] >= 1
        assert "Bombay (Oh)" in analytics["rare_blood_group_statistics"]


if __name__ == "__main__":
    test_full_pipeline()
    print("All integration tests passed successfully.")
