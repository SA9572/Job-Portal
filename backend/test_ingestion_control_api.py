from fastapi.testclient import TestClient

from app.api.main import app
from app.database.config import SessionLocal
from app.database.ingestion_run_model import IngestionRunModel


if __name__ == "__main__":
    print("========== INGESTION CONTROL API TEST ==========")

    client = TestClient(app)

# =========================================
# TEST 1: INVALID BOUNDS PARAMETERS (400)
# =========================================

print()
print("========== TEST 1: INVALID PARAMETERS (400) ==========")

response = client.post("/api/ingestion/run", json={"max_pages": 50, "page_size": 20})
print("Max pages > 20 status:", response.status_code)
assert response.status_code == 400

response = client.post("/api/ingestion/run", json={"max_pages": 5, "page_size": 200})
print("Page size > 100 status:", response.status_code)
assert response.status_code == 400

# =========================================
# TEST 2: CONCURRENCY CONFLICT (409)
# =========================================

print()
print("========== TEST 2: CONCURRENCY CHECK (409) ==========")

session = SessionLocal()

try:

    # Create a temporary running status run
    active_run = IngestionRunModel(
        source="test_concurrency",
        started_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        status="running",
    )
    session.add(active_run)
    session.commit()

    response = client.post("/api/ingestion/run", json={"max_pages": 1, "page_size": 5})

    print("Concurrency conflict status:", response.status_code)
    err_msg = response.json().get("error", {}).get("message") or response.json().get("detail")
    print("Detail/Message:", err_msg)

    assert response.status_code == 409
    assert err_msg == "An ingestion run is currently in progress"

    # Cleanup active run
    session.delete(active_run)
    session.commit()

finally:

    session.close()

# =========================================
# TEST 3: SUCCESSFUL CONTROLLED INGESTION RUN
# =========================================

print()
print("========== TEST 3: SUCCESSFUL TRIGGER ==========")

response = client.post("/api/ingestion/run", json={"max_pages": 1, "page_size": 5})

print("Status:", response.status_code)

data = response.json()

print("Message:", data["message"])
print("Source:", data["source"])
print("Pages attempted:", data["pages_attempted"])
print("Jobs fetched:", data["jobs_fetched"])
print("Jobs new:", data["jobs_new"])
print("Jobs duplicate:", data["jobs_duplicate"])
print("Jobs changed:", data["jobs_changed"])

assert response.status_code == 200
assert data["source"] == "himalayas"
assert data["pages_attempted"] == 1
assert "jobs_fetched" in data

print()
print("========== INGESTION CONTROL API TEST COMPLETED ==========")
