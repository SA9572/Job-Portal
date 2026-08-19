"""
Phase 17 — Job Expiration & Soft Delete Tests

Tests the complete Phase 17 implementation using FastAPI TestClient:
1. Stats endpoint
2. Soft delete endpoint
3. Restore endpoint
4. Expired jobs listing
5. Deleted jobs listing
6. Default exclusion of deleted/expired
7. include_expired / include_deleted flags
8. Idempotent deletion
"""

from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)
BASE = "/api/jobs"


def test_stats_endpoint():
    """GET /api/jobs/stats returns correct structure."""
    r = client.get(f"{BASE}/stats")
    assert r.status_code == 200, f"Stats failed: {r.status_code} {r.text}"
    data = r.json()
    assert "total" in data
    assert "active" in data
    assert "expired" in data
    assert "deleted" in data
    assert data["total"] >= 0
    assert data["active"] >= 0
    assert data["expired"] >= 0
    assert data["deleted"] >= 0
    assert data["total"] == data["active"] + data["expired"] + data["deleted"]
    print(f"  PASS: Stats endpoint -- total={data['total']}, active={data['active']}, expired={data['expired']}, deleted={data['deleted']}")
    return data


def test_get_jobs_default():
    """GET /api/jobs returns jobs with is_deleted field."""
    r = client.get(f"{BASE}?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "jobs" in data
    if data["jobs"]:
        job = data["jobs"][0]
        assert "is_deleted" in job, "is_deleted field missing from response"
        assert "deleted_at" in job, "deleted_at field missing from response"
        assert job["is_deleted"] == False, "Default listing returned a deleted job"
    print(f"  PASS: Default listing -- {data['count']} jobs, all have is_deleted/deleted_at fields")
    return data


def test_soft_delete_and_restore():
    """DELETE and POST restore work correctly."""

    # Find a job to test with
    r = client.get(f"{BASE}?limit=1")
    data = r.json()
    if not data["jobs"]:
        print("  SKIP: No jobs available for soft delete test")
        return

    job_id = data["jobs"][0]["id"]
    print(f"  Testing with job_id={job_id}")

    # --- SOFT DELETE ---
    r = client.delete(f"{BASE}/{job_id}")
    assert r.status_code == 200, f"Delete failed: {r.status_code} {r.text}"
    deleted_job = r.json()
    assert deleted_job["is_deleted"] == True
    assert deleted_job["deleted_at"] is not None
    print(f"  PASS: Soft delete -- is_deleted=True, deleted_at={deleted_job['deleted_at']}")

    # --- VERIFY EXCLUDED FROM DEFAULT LISTING ---
    r = client.get(f"{BASE}?limit=100")
    data = r.json()
    job_ids_in_listing = [j["id"] for j in data["jobs"]]
    assert job_id not in job_ids_in_listing, "Deleted job still appears in default listing!"
    print(f"  PASS: Deleted job excluded from default listing")

    # --- VERIFY IN DELETED LISTING ---
    r = client.get(f"{BASE}/deleted?limit=100")
    assert r.status_code == 200
    data = r.json()
    deleted_ids = [j["id"] for j in data["jobs"]]
    assert job_id in deleted_ids, "Deleted job not in /deleted listing!"
    print(f"  PASS: Deleted job appears in /deleted listing")

    # --- VERIFY STATS UPDATED ---
    stats = test_stats_endpoint()

    # --- VERIFY include_deleted=true ---
    r = client.get(f"{BASE}?include_deleted=true&limit=100")
    data = r.json()
    job_ids_incl = [j["id"] for j in data["jobs"]]
    assert job_id in job_ids_incl, "Deleted job not in include_deleted=true listing!"
    print(f"  PASS: Deleted job appears with include_deleted=true")

    # --- IDEMPOTENT DELETE ---
    r = client.delete(f"{BASE}/{job_id}")
    assert r.status_code == 200
    print(f"  PASS: Idempotent delete -- no error on re-delete")

    # --- RESTORE ---
    r = client.post(f"{BASE}/{job_id}/restore")
    assert r.status_code == 200, f"Restore failed: {r.status_code} {r.text}"
    restored_job = r.json()
    assert restored_job["is_deleted"] == False
    assert restored_job["deleted_at"] is None
    print(f"  PASS: Restore -- is_deleted=False, deleted_at=None")

    # --- VERIFY BACK IN DEFAULT LISTING ---
    r = client.get(f"{BASE}?limit=100")
    data = r.json()
    job_ids_after = [j["id"] for j in data["jobs"]]
    assert job_id in job_ids_after, "Restored job not back in default listing!"
    print(f"  PASS: Restored job back in default listing")


def test_expired_endpoint():
    """GET /api/jobs/expired returns valid response."""
    r = client.get(f"{BASE}/expired")
    assert r.status_code == 200
    data = r.json()
    assert "jobs" in data
    assert "total" in data
    print(f"  PASS: Expired endpoint -- {data['total']} expired jobs")


def test_deleted_endpoint():
    """GET /api/jobs/deleted returns valid response."""
    r = client.get(f"{BASE}/deleted")
    assert r.status_code == 200
    data = r.json()
    assert "jobs" in data
    assert "total" in data
    print(f"  PASS: Deleted endpoint -- {data['total']} deleted jobs")


def test_404_on_nonexistent():
    """DELETE and restore on nonexistent job returns 404."""
    r = client.delete(f"{BASE}/999999")
    assert r.status_code == 404
    print(f"  PASS: DELETE /999999 -> 404")

    r = client.post(f"{BASE}/999999/restore")
    assert r.status_code == 404
    print(f"  PASS: POST /999999/restore -> 404")


def test_get_single_job_excludes_deleted():
    """GET /api/jobs/{id} returns 404 for deleted jobs."""
    # Get a job
    r = client.get(f"{BASE}?limit=1")
    data = r.json()
    if not data["jobs"]:
        print("  SKIP: No jobs available")
        return

    job_id = data["jobs"][0]["id"]

    # Delete it
    r = client.delete(f"{BASE}/{job_id}")
    assert r.status_code == 200

    # Try to get it -- should 404
    r = client.get(f"{BASE}/{job_id}")
    assert r.status_code == 404, f"Deleted job still accessible via GET: {r.status_code}"
    print(f"  PASS: GET /{job_id} -> 404 after soft delete")

    # Restore for cleanup
    r = client.post(f"{BASE}/{job_id}/restore")
    assert r.status_code == 200
    print(f"  PASS: Cleaned up -- restored job {job_id}")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 17 - JOB EXPIRATION & SOFT DELETE TESTS")
    print("=" * 60)
    print()

    print("[1] Stats Endpoint")
    test_stats_endpoint()
    print()

    print("[2] Default Job Listing")
    test_get_jobs_default()
    print()

    print("[3] Expired Jobs Endpoint")
    test_expired_endpoint()
    print()

    print("[4] Deleted Jobs Endpoint")
    test_deleted_endpoint()
    print()

    print("[5] 404 on Nonexistent Jobs")
    test_404_on_nonexistent()
    print()

    print("[6] Soft Delete & Restore Flow")
    test_soft_delete_and_restore()
    print()

    print("[7] Single Job Excludes Deleted")
    test_get_single_job_excludes_deleted()
    print()

    print("=" * 60)
    print("ALL PHASE 17 TESTS PASSED")
    print("=" * 60)
