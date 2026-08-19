from fastapi.testclient import TestClient

from app.api.main import app


print("========== INGESTION RUN API TEST ==========")

client = TestClient(app)

# =========================================
# TEST 1: GET INGESTION RUNS LIST
# =========================================

print()
print("========== TEST 1: GET INGESTION RUNS LIST ==========")

response = client.get("/api/ingestion/runs?limit=5&offset=0")

print("Status:", response.status_code)

data = response.json()

print("Count:", data["count"])
print("Total:", data["total"])
print("Runs returned:", len(data["runs"]))

assert response.status_code == 200
assert data["count"] > 0
assert data["total"] > 0
assert len(data["runs"]) > 0

first_run = data["runs"][0]

print("First run ID:", first_run["id"])
print("Source:", first_run["source"])
print("Status:", first_run["status"])
print("Pages attempted:", first_run["pages_attempted"])
print("Jobs fetched:", first_run["jobs_fetched"])
print("Jobs new:", first_run["jobs_new"])
print("Jobs duplicate:", first_run["jobs_duplicate"])
print("Jobs changed:", first_run["jobs_changed"])

assert "id" in first_run
assert "source" in first_run
assert "status" in first_run
assert "started_at" in first_run

valid_run_id = first_run["id"]

# =========================================
# TEST 2: FILTER RUNS BY STATUS
# =========================================

print()
print("========== TEST 2: FILTER BY STATUS ==========")

response = client.get("/api/ingestion/runs?status=success")

print("Status:", response.status_code)

filtered = response.json()

print("Matching success runs:", filtered["total"])

assert response.status_code == 200
for r in filtered["runs"]:
    assert r["status"] == "success"

# =========================================
# TEST 3: FILTER RUNS BY SOURCE
# =========================================

print()
print("========== TEST 3: FILTER BY SOURCE ==========")

response = client.get("/api/ingestion/runs?source=himalayas")

print("Status:", response.status_code)

filtered_src = response.json()

print("Matching himalayas runs:", filtered_src["total"])

assert response.status_code == 200
for r in filtered_src["runs"]:
    assert r["source"] == "himalayas"

# =========================================
# TEST 4: GET SINGLE INGESTION RUN
# =========================================

print()
print("========== TEST 4: GET SINGLE RUN DETAILS ==========")

response = client.get(f"/api/ingestion/runs/{valid_run_id}")

print("Status:", response.status_code)

single = response.json()

print("Run ID:", single["id"])
print("Status:", single["status"])

assert response.status_code == 200
assert single["id"] == valid_run_id

# =========================================
# TEST 5: RUN NOT FOUND (404)
# =========================================

print()
print("========== TEST 5: RUN NOT FOUND (404) ==========")

response = client.get("/api/ingestion/runs/9999999")

print("Status:", response.status_code)

assert response.status_code == 404
err_msg = response.json().get("error", {}).get("message") or response.json().get("detail")
assert err_msg == "Ingestion run not found"

print()
print("========== INGESTION RUN API TEST COMPLETED ==========")
