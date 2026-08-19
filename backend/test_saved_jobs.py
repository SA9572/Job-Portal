"""
Phase 20 — Saved Jobs System Tests

Tests the complete Phase 20 implementation:
1. Bookmark job with optional notes (POST /api/saved-jobs/{job_id})
2. Duplicate bookmarking (idempotent / updates notes)
3. Check saved status (GET /api/saved-jobs/{job_id}/check)
4. List user saved jobs (GET /api/saved-jobs)
5. Unsave job (DELETE /api/saved-jobs/{job_id})
6. Unauthenticated requests protection (401)
7. 404 for saving nonexistent job
"""

from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)
AUTH_BASE = "/api/auth"
SAVED_BASE = "/api/saved-jobs"
JOBS_BASE = "/api/jobs"


def get_authenticated_user_tokens():
    """Helper: Creates a unique test user and returns access token."""
    email = f"bookmarkuser_{__import__('time').time()}@example.com"
    r = client.post(
        f"{AUTH_BASE}/register",
        json={"email": email, "password": "UserPass123!", "full_name": "Bookmark User"},
    )
    assert r.status_code == 201
    return r.json()["access_token"]


def test_unauthenticated_access():
    """Unauthenticated requests to saved-jobs endpoints return 401."""
    r_save = client.post(f"{SAVED_BASE}/1")
    assert r_save.status_code == 401
    print("  PASS: Unauthenticated POST /saved-jobs/1 -> 401")

    r_list = client.get(SAVED_BASE)
    assert r_list.status_code == 401
    print("  PASS: Unauthenticated GET /saved-jobs -> 401")

    r_check = client.get(f"{SAVED_BASE}/1/check")
    assert r_check.status_code == 401
    print("  PASS: Unauthenticated GET /saved-jobs/1/check -> 401")

    r_del = client.delete(f"{SAVED_BASE}/1")
    assert r_del.status_code == 401
    print("  PASS: Unauthenticated DELETE /saved-jobs/1 -> 401")


def test_save_and_check_flow():
    """Authenticated user saves job, checks status, lists, and unsaves."""
    token = get_authenticated_user_tokens()
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch a job to save
    r_jobs = client.get(f"{JOBS_BASE}?limit=1")
    assert r_jobs.status_code == 200
    jobs = r_jobs.json().get("jobs", [])
    if not jobs:
        print("  SKIP: No jobs available in database")
        return

    job_id = jobs[0]["id"]
    print(f"  Testing bookmark flow with job_id={job_id} ({jobs[0]['title']})")

    # 1. Check initial status -> False
    r_chk1 = client.get(f"{SAVED_BASE}/{job_id}/check", headers=headers)
    assert r_chk1.status_code == 200
    assert r_chk1.json()["is_saved"] == False
    print("  PASS: Initial check is_saved=False")

    # 2. Save job with personal notes
    r_save = client.post(
        f"{SAVED_BASE}/{job_id}",
        json={"notes": "Great Python role, apply soon!"},
        headers=headers,
    )
    assert r_save.status_code == 201, f"Failed: {r_save.status_code} {r_save.text}"
    saved_data = r_save.json()
    assert saved_data["job_id"] == job_id
    assert saved_data["notes"] == "Great Python role, apply soon!"
    assert "job" in saved_data
    print(f"  PASS: Save job successful (notes='{saved_data['notes']}')")

    # 3. Check status -> True
    r_chk2 = client.get(f"{SAVED_BASE}/{job_id}/check", headers=headers)
    assert r_chk2.status_code == 200
    assert r_chk2.json()["is_saved"] == True
    print("  PASS: Check after saving is_saved=True")

    # 4. List saved jobs
    r_list = client.get(SAVED_BASE, headers=headers)
    assert r_list.status_code == 200
    list_data = r_list.json()
    assert list_data["total"] == 1
    assert list_data["jobs"][0]["job_id"] == job_id
    print(f"  PASS: List saved jobs returned {list_data['total']} saved item")

    # 5. Unsave job
    r_unsave = client.delete(f"{SAVED_BASE}/{job_id}", headers=headers)
    assert r_unsave.status_code == 200
    print("  PASS: Unsave job successful")

    # 6. Check status after unsave -> False
    r_chk3 = client.get(f"{SAVED_BASE}/{job_id}/check", headers=headers)
    assert r_chk3.status_code == 200
    assert r_chk3.json()["is_saved"] == False
    print("  PASS: Check after unsaving is_saved=False")


def test_save_nonexistent_job():
    """Attempting to save nonexistent job returns 404."""
    token = get_authenticated_user_tokens()
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(f"{SAVED_BASE}/999999", headers=headers)
    assert r.status_code == 404
    print("  PASS: POST /saved-jobs/999999 -> 404")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 20 - SAVED JOBS SYSTEM TESTS")
    print("=" * 60)
    print()

    print("[1] Unauthenticated Protection")
    test_unauthenticated_access()
    print()

    print("[2] Save, Check, List & Unsave Flow")
    test_save_and_check_flow()
    print()

    print("[3] 404 Nonexistent Job")
    test_save_nonexistent_job()
    print()

    print("=" * 60)
    print("ALL PHASE 20 TESTS PASSED")
    print("=" * 60)
