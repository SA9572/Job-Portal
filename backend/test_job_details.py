from fastapi.testclient import TestClient

from app.api.main import app


print("========== JOB DETAILS API TEST ==========")

client = TestClient(app)

# =========================================
# TEST 1: GET SINGLE JOB (VALID ID)
# =========================================

print()
print("========== TEST 1: GET VALID JOB ==========")

# First get a valid job ID from list endpoint
list_resp = client.get("/api/jobs?limit=1")
assert list_resp.status_code == 200
list_data = list_resp.json()
assert len(list_data["jobs"]) > 0

valid_job_id = list_data["jobs"][0]["id"]

response = client.get(f"/api/jobs/{valid_job_id}")

print("Status:", response.status_code)

job = response.json()

print("Job ID:", job["id"])
print("Title:", job["title"])
print("Company:", job["company"])
print("Source:", job["source"])
print("Application URL:", job["application_url"])

assert response.status_code == 200
assert job["id"] == valid_job_id
assert isinstance(job["title"], str) and len(job["title"]) > 0
assert isinstance(job["company"], str) and len(job["company"]) > 0
assert isinstance(job["description"], str) and len(job["description"]) > 0
assert "created_at" in job
assert "updated_at" in job
assert "fetched_at" in job

# Verify NULL handling: null fields remain None/null, not fabricated strings
if job["expires_at"] is None:
    print("expires_at is correctly null")

# =========================================
# TEST 2: GET NON-EXISTENT JOB (404)
# =========================================

print()
print("========== TEST 2: GET NON-EXISTENT JOB (404) ==========")

response = client.get("/api/jobs/9999999")

print("Status:", response.status_code)
err_msg = response.json().get("error", {}).get("message") or response.json().get("detail")
print("Detail/Message:", err_msg)

assert response.status_code == 404
assert err_msg == "Job not found"

# =========================================
# TEST 3: INVALID JOB ID FORMAT (422)
# =========================================

print()
print("========== TEST 3: INVALID JOB ID FORMAT (422) ==========")

response = client.get("/api/jobs/invalid_id_string")

print("Status:", response.status_code)

assert response.status_code == 422

print()
print("========== JOB DETAILS API TEST COMPLETED ==========")
