from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)

print("========== RESPONSE SCHEMA TEST ==========")

# =========================================
# TEST 1: GET /health
# =========================================

print()
print("========== TEST 1: GET /health ==========")

response = client.get("/health")

print("Status:", response.status_code)
print("Response:", response.json())

assert response.status_code == 200
assert response.json() == {
    "status": "ok",
    "service": "job-required-api",
}

# =========================================
# TEST 2: GET /api/jobs/test
# =========================================

print()
print("========== TEST 2: GET /api/jobs/test ==========")

response = client.get("/api/jobs/test")

print("Status:", response.status_code)
print("Response:", response.json())

assert response.status_code == 200
assert response.json() == {
    "message": "Jobs API is working"
}

# =========================================
# TEST 3: GET /api/jobs LIST RESPONSE SCHEMA
# =========================================

print()
print("========== TEST 3: GET /api/jobs SCHEMA ==========")

response = client.get("/api/jobs?limit=2&offset=0")

print("Status:", response.status_code)

data = response.json()

print("Keys in response:", list(data.keys()))
print("Count:", data["count"])
print("Total:", data["total"])
print("Limit:", data["limit"])
print("Offset:", data["offset"])
print("Jobs count:", len(data["jobs"]))

assert response.status_code == 200
assert "count" in data
assert "total" in data
assert "limit" in data
assert "offset" in data
assert "jobs" in data

if data["jobs"]:
    job = data["jobs"][0]

    print()
    print("First job keys:", sorted(job.keys()))
    print("Job ID:", job["id"])
    print("Title:", job["title"])
    print("Company:", job["company"])

    assert "id" in job
    assert "source" in job
    assert "external_id" in job
    assert "title" in job
    assert "company" in job
    assert "description" in job

# =========================================
# TEST 4: GET /api/jobs/{job_id} SINGLE RESPONSE SCHEMA
# =========================================

print()
print("========== TEST 4: GET /api/jobs/{job_id} SCHEMA ==========")

if data["jobs"]:
    job_id = data["jobs"][0]["id"]

    response = client.get(f"/api/jobs/{job_id}")

    print("Status:", response.status_code)

    single_job = response.json()

    print("Single job ID:", single_job["id"])
    print("Single job title:", single_job["title"])

    assert response.status_code == 200
    assert single_job["id"] == job_id

# =========================================
# TEST 5: GET /api/jobs/999999 NOT FOUND
# =========================================

print()
print("========== TEST 5: NOT FOUND 404 ==========")

response = client.get("/api/jobs/999999")

print("Status:", response.status_code)
err_msg = response.json().get("error", {}).get("message") or response.json().get("detail")
print("Detail/Message:", err_msg)

assert response.status_code == 404

print()
print("========== RESPONSE SCHEMA TEST COMPLETED ==========")
