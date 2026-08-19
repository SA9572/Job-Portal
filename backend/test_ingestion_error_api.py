from fastapi.testclient import TestClient

from app.api.main import app
from app.database.config import SessionLocal
from app.database.ingestion_error_model import IngestionErrorModel
from app.database.ingestion_run_model import IngestionRunModel


print("========== INGESTION ERROR API TEST ==========")

client = TestClient(app)

session = SessionLocal()

try:

    # Find a run with errors
    sample_error = session.query(IngestionErrorModel).first()

    if sample_error:

        run_id = sample_error.ingestion_run_id

        print(f"Testing errors for run_id={run_id}")

        # =========================================
        # TEST 1: GET INGESTION ERRORS FOR RUN
        # =========================================

        print()
        print("========== TEST 1: GET INGESTION ERRORS LIST ==========")

        response = client.get(f"/api/ingestion/runs/{run_id}/errors")

        print("Status:", response.status_code)

        data = response.json()

        print("Count:", data["count"])
        print("Total:", data["total"])
        print("Errors returned:", len(data["errors"]))

        assert response.status_code == 200
        assert data["count"] > 0
        assert data["total"] > 0
        assert len(data["errors"]) > 0

        first_err = data["errors"][0]

        print("First error ID:", first_err["id"])
        print("Run ID:", first_err["ingestion_run_id"])
        print("Page:", first_err["page_number"])
        print("Offset:", first_err["offset"])
        print("Error type:", first_err["error_type"])
        print("Message:", first_err["message"])

        assert "id" in first_err
        assert first_err["ingestion_run_id"] == run_id
        assert "page_number" in first_err
        assert "attempts" in first_err
        assert "error_type" in first_err
        assert "message" in first_err
        assert "occurred_at" in first_err

    # Find a successful run with 0 errors
    success_run = (
        session.query(IngestionRunModel)
        .filter(IngestionRunModel.status == "success")
        .first()
    )

    if success_run:

        print()
        print(f"========== TEST 2: GET ERRORS FOR SUCCESS RUN (run_id={success_run.id}) ==========")

        response = client.get(f"/api/ingestion/runs/{success_run.id}/errors")

        print("Status:", response.status_code)

        data = response.json()

        print("Count:", data["count"])
        print("Total:", data["total"])

        assert response.status_code == 200
        assert data["count"] == 0
        assert data["total"] == 0
        assert data["errors"] == []

    # =========================================
    # TEST 3: RUN NOT FOUND (404)
    # =========================================

    print()
    print("========== TEST 3: RUN NOT FOUND (404) ==========")

    response = client.get("/api/ingestion/runs/9999999/errors")

    print("Status:", response.status_code)

    assert response.status_code == 404
    err_msg = response.json().get("error", {}).get("message") or response.json().get("detail")
    assert err_msg == "Ingestion run not found"

finally:

    session.close()

print()
print("========== INGESTION ERROR API TEST COMPLETED ==========")
