"""
==============================================================================
LifeLine Crisis Surge Load Testing Suite (Locust)
==============================================================================
Simulates 100 to 1000 concurrent users searching for ultra-rare blood phenotypes,
fetching emergency transfusion feeds, and submitting urgent blood requisitions.

Quick Execution Commands:
------------------------------------------------------------------------------
1. Install Locust:
   pip install locust

2. Run Interactive Web UI:
   locust -f locustfile.py --host=http://127.0.0.1:8000
   Open: http://localhost:8089 in your browser

3. Headless 100 Users Benchmark (with HTML report & graphs):
   locust -f locustfile.py --headless -u 100 -r 10 --run-time 2m \
          --host=http://127.0.0.1:8000 \
          --html=reports/loadtest_100_users.html \
          --csv=reports/loadtest_100_users

4. Headless 500 Users Stress Test:
   locust -f locustfile.py --headless -u 500 -r 25 --run-time 3m \
          --host=http://127.0.0.1:8000 \
          --html=reports/loadtest_500_users.html \
          --csv=reports/loadtest_500_users

5. Headless 1,000 Users Crisis Surge Spike Test:
   locust -f locustfile.py --headless -u 1000 -r 50 --run-time 5m \
          --host=http://127.0.0.1:8000 \
          --html=reports/loadtest_1000_users.html \
          --csv=reports/loadtest_1000_users
==============================================================================
"""

import random
import uuid
from locust import HttpUser, task, between, events

# Target Blood Groups with high weighting on rare phenotypes
BLOOD_GROUPS = [
    "Bombay (Oh)",
    "Rh-null",
    "Duffy Null Fy(a-b-)",
    "Kell Null (K0)",
    "O-",
    "O+",
    "A-",
    "A+",
    "B-",
    "B+",
    "AB-",
    "AB+",
]

CITIES = ["Palo Alto", "New York", "Chicago", "Seattle", "Austin", "Boston", "San Francisco"]


class LifeLineEmergencyUser(HttpUser):
    # Simulated think time between user actions during emergency crisis
    wait_time = between(0.5, 2.0)
    token = None
    hospital_id = None

    def on_start(self):
        """
        Executed on spawn: Authenticates or registers a simulated test user
        to test JWT verification and database connection pooling.
        """
        email = f"loadtest_user_{uuid.uuid4().hex[:8]}@lifeline.org"
        phone = f"+1555{random.randint(1000000, 9999999)}"

        # Register User
        reg_payload = {
            "name": f"Surge User {email[:8]}",
            "email": email,
            "phone": phone,
            "role": random.choice(["donor", "patient", "hospital"]),
            "password": "Password123!",
        }
        res = self.client.post("/api/v1/auth/register", json=reg_payload)

        # Login to obtain JWT Bearer Token
        if res.status_code in [200, 201]:
            login_res = self.client.post("/api/v1/auth/login", json={
                "email": email,
                "password": "Password123!",
            })
            if login_res.status_code == 200:
                self.token = login_res.json().get("access_token")

        # Fetch an existing hospital ID for posting blood requests
        hosp_res = self.client.get("/api/v1/hospitals/")
        if hosp_res.status_code == 200 and len(hosp_res.json()) > 0:
            self.hospital_id = hosp_res.json()[0]["id"]

    def auth_headers(self):
        """Returns bearer token headers if authenticated."""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    # --------------------------------------------------------------------------
    # Task 1: Health Check (Highest Frequency - Used by ALB Target Groups)
    # --------------------------------------------------------------------------
    @task(10)
    def check_health(self):
        with self.client.get("/api/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed with HTTP {response.status_code}")

    # --------------------------------------------------------------------------
    # Task 2: Search Ultra-Rare and Standard Blood Groups (Simulates Donor Lookup)
    # --------------------------------------------------------------------------
    @task(8)
    def search_rare_blood_donors(self):
        target_group = random.choice(BLOOD_GROUPS)
        target_city = random.choice(CITIES) if random.random() > 0.4 else ""

        url = f"/api/v1/donors/?blood_group={target_group}"
        if target_city:
            url += f"&city={target_city}"

        with self.client.get(url, catch_response=True, name="/api/v1/donors/ [Search Blood Group]") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Search donors failed: HTTP {response.status_code}")

    # --------------------------------------------------------------------------
    # Task 3: Browse Live Emergency Requests Feed (High Public Read Traffic)
    # --------------------------------------------------------------------------
    @task(6)
    def view_emergency_feed(self):
        status_filter = random.choice(["open", "matched", ""])
        url = "/api/v1/blood-requests/"
        if status_filter:
            url += f"?status={status_filter}"

        with self.client.get(url, catch_response=True, name="/api/v1/blood-requests/ [Live Feed]") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Live feed query failed: HTTP {response.status_code}")

    # --------------------------------------------------------------------------
    # Task 4: Post Emergency SOS Blood Request (Write Heavy - Triggers SNS Alerts)
    # --------------------------------------------------------------------------
    @task(3)
    def create_emergency_sos_request(self):
        if not self.hospital_id:
            return

        payload = {
            "hospital_id": self.hospital_id,
            "patient_name": f"Surge Trauma Patient {random.randint(100, 999)}",
            "blood_group": random.choice(BLOOD_GROUPS),
            "units_required": random.randint(1, 4),
            "urgency_level": random.choice(["critical", "high", "moderate"]),
        }

        with self.client.post(
            "/api/v1/blood-requests/",
            json=payload,
            headers=self.auth_headers(),
            catch_response=True,
            name="/api/v1/blood-requests/ [Post Emergency SOS]"
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"SOS broadcast failed: HTTP {response.status_code}")

    # --------------------------------------------------------------------------
    # Task 5: Request S3 Presigned Upload URL for Medical Records
    # --------------------------------------------------------------------------
    @task(2)
    def request_s3_presigned_url(self):
        payload = {
            "file_name": f"health_cert_{uuid.uuid4().hex[:6]}.pdf",
            "file_type": "application/pdf",
            "document_type": "health_clearance",
        }

        with self.client.post(
            "/api/v1/documents/upload-url",
            json=payload,
            headers=self.auth_headers(),
            catch_response=True,
            name="/api/v1/documents/upload-url [Presigned S3 URL]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Presigned URL generation failed: HTTP {response.status_code}")

    # --------------------------------------------------------------------------
    # Task 6: View Verified Hospitals
    # --------------------------------------------------------------------------
    @task(2)
    def list_verified_hospitals(self):
        with self.client.get("/api/v1/hospitals/", catch_response=True, name="/api/v1/hospitals/ [List]") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to list hospitals: HTTP {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n=======================================================")
    print("🔥 LifeLine Crisis Surge Load Test Initialized")
    print("Simulating concurrent donor searches & emergency SOS requests")
    print("=======================================================\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n=======================================================")
    print("🏁 LifeLine Crisis Surge Load Test Completed")
    print("Review HTML and CSV reports for latency percentiles (p50, p95, p99)")
    print("=======================================================\n")
