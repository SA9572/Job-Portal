from fastapi.testclient import TestClient

from app.api.main import app
from app.database.config import SessionLocal
from app.database.job_change_model import JobChangeModel


print("========== JOB CHANGE API TEST ==========")

client = TestClient(app)

session = SessionLocal()

try:

    # Find a job with changes in database
    sample_change = session.query(JobChangeModel).first()

    if sample_change:

        job_id = sample_change.job_id
        change_id = sample_change.id

        print(f"Testing with job_id={job_id}, change_id={change_id}")

        # =========================================
        # TEST 1: GET JOB CHANGES LIST
        # =========================================

        print()
        print("========== TEST 1: GET JOB CHANGES LIST ==========")

        response = client.get(f"/api/jobs/{job_id}/changes")

        print("Status:", response.status_code)

        data = response.json()

        print("Count:", data["count"])
        print("Total:", data["total"])
        print("Changes returned:", len(data["changes"]))

        assert response.status_code == 200
        assert data["count"] > 0
        assert data["total"] > 0
        assert len(data["changes"]) > 0

        first_change = data["changes"][0]

        print("First change ID:", first_change["id"])
        print("Old hash:", first_change["old_content_hash"])
        print("New hash:", first_change["new_content_hash"])

        assert "id" in first_change
        assert "job_id" in first_change
        assert "old_content_hash" in first_change
        assert "new_content_hash" in first_change
        assert "changed_at" in first_change

        # =========================================
        # TEST 2: GET SINGLE JOB CHANGE
        # =========================================

        print()
        print("========== TEST 2: GET SINGLE JOB CHANGE ==========")

        response = client.get(f"/api/jobs/{job_id}/changes/{change_id}")

        print("Status:", response.status_code)

        single = response.json()

        print("Single change ID:", single["id"])
        print("Old hash:", single["old_content_hash"])
        print("New hash:", single["new_content_hash"])

        assert response.status_code == 200
        assert single["id"] == change_id
        assert single["job_id"] == job_id

        # =========================================
        # TEST 3: JOB NOT FOUND (404)
        # =========================================

        print()
        print("========== TEST 3: JOB NOT FOUND (404) ==========")

        response = client.get("/api/jobs/9999999/changes")

        print("Status:", response.status_code)

        assert response.status_code == 404
        err_msg3 = response.json().get("error", {}).get("message") or response.json().get("detail")
        assert err_msg3 == "Job not found"

        # =========================================
        # TEST 4: CHANGE NOT FOUND (404)
        # =========================================

        print()
        print("========== TEST 4: CHANGE NOT FOUND (404) ==========")

        response = client.get(f"/api/jobs/{job_id}/changes/9999999")

        print("Status:", response.status_code)

        assert response.status_code == 404
        err_msg4 = response.json().get("error", {}).get("message") or response.json().get("detail")
        assert err_msg4 == "Job change record not found"

    else:

        print("No job changes present in database to query.")

finally:

    session.close()

print()
print("========== JOB CHANGE API TEST COMPLETED ==========")
