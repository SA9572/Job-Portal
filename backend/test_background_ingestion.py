import time
from fastapi.testclient import TestClient

from app.api.main import app
from app.ingestion.scheduler import IngestionScheduler


if __name__ == "__main__":
    print("========== BACKGROUND INGESTION TEST ==========")

    client = TestClient(app)

# =========================================
# TEST 1: POST /api/ingestion/run-async (202)
# =========================================

print()
print("========== TEST 1: TRIGGER ASYNC INGESTION ==========")

response = client.post("/api/ingestion/run-async", json={"max_pages": 1, "page_size": 5})

print("Status:", response.status_code)

data = response.json()

print("Response:", data)

assert response.status_code == 202
assert data["status"] == "accepted"
assert data["message"] == "Ingestion job started in background"

# Sleep briefly to allow background task to complete
time.sleep(3)

# =========================================
# TEST 2: INGESTION SCHEDULER CLASS
# =========================================

print()
print("========== TEST 2: INGESTION SCHEDULER CLASS ==========")

scheduler = IngestionScheduler(interval_minutes=1, max_pages=1, page_size=5)

assert not scheduler.is_running()

scheduler.start()
print("Scheduler started. Running:", scheduler.is_running())
assert scheduler.is_running()

scheduler.stop()
print("Scheduler stopped. Running:", scheduler.is_running())
assert not scheduler.is_running()

print()
print("========== BACKGROUND INGESTION TEST COMPLETED ==========")
