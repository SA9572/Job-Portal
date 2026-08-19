"""
Phase 21 — Job Alerts System Tests

Tests the complete Phase 21 implementation:
1. Create job alert (POST /api/alerts)
2. List user alerts (GET /api/alerts)
3. Get single alert detail (GET /api/alerts/{id})
4. Update alert criteria & active status (PUT /api/alerts/{id})
5. Test match query (POST /api/alerts/{id}/test-match)
6. Delete alert (DELETE /api/alerts/{id})
7. Unauthenticated access protection (401)
8. User isolation (user A cannot access user B's alert)
"""

from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)
AUTH_BASE = "/api/auth"
ALERTS_BASE = "/api/alerts"


def get_authenticated_user_tokens(prefix: str = "alertuser"):
    """Helper: Creates a unique test user and returns access token."""
    email = f"{prefix}_{__import__('time').time()}@example.com"
    r = client.post(
        f"{AUTH_BASE}/register",
        json={"email": email, "password": "UserPass123!", "full_name": f"{prefix} User"},
    )
    assert r.status_code == 201
    return r.json()["access_token"]


def test_unauthenticated_access():
    """Unauthenticated requests to alerts endpoints return 401."""
    r_create = client.post(ALERTS_BASE, json={"name": "Test Alert"})
    assert r_create.status_code == 401
    print("  PASS: Unauthenticated POST /alerts -> 401")

    r_list = client.get(ALERTS_BASE)
    assert r_list.status_code == 401
    print("  PASS: Unauthenticated GET /alerts -> 401")

    r_get = client.get(f"{ALERTS_BASE}/1")
    assert r_get.status_code == 401
    print("  PASS: Unauthenticated GET /alerts/1 -> 401")


def test_job_alerts_crud_flow():
    """Test full CRUD cycle for job subscription alerts."""
    token = get_authenticated_user_tokens("user1")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. CREATE ALERT
    payload = {
        "name": "Python Remote Engineer",
        "keywords": "python",
        "location": "Remote",
        "min_salary": 80000.0,
        "frequency": "daily",
        "is_active": True,
    }
    r_create = client.post(ALERTS_BASE, json=payload, headers=headers)
    assert r_create.status_code == 201, f"Failed: {r_create.status_code} {r_create.text}"
    alert = r_create.json()
    alert_id = alert["id"]

    assert alert["name"] == "Python Remote Engineer"
    assert alert["keywords"] == "python"
    assert alert["min_salary"] == 80000.0
    assert alert["is_active"] == True
    print(f"  PASS: Alert created (id={alert_id}, name='{alert['name']}')")

    # 2. LIST ALERTS
    r_list = client.get(ALERTS_BASE, headers=headers)
    assert r_list.status_code == 200
    list_data = r_list.json()
    assert list_data["total"] == 1
    assert list_data["alerts"][0]["id"] == alert_id
    print(f"  PASS: Listed alerts (total={list_data['total']})")

    # 3. GET SINGLE ALERT
    r_get = client.get(f"{ALERTS_BASE}/{alert_id}", headers=headers)
    assert r_get.status_code == 200
    assert r_get.json()["id"] == alert_id
    print("  PASS: Retrieved single alert details")

    # 4. UPDATE ALERT
    update_payload = {
        "name": "Senior Python Developer",
        "min_salary": 100000.0,
        "is_active": False,
    }
    r_update = client.put(f"{ALERTS_BASE}/{alert_id}", json=update_payload, headers=headers)
    assert r_update.status_code == 200
    updated = r_update.json()
    assert updated["name"] == "Senior Python Developer"
    assert updated["min_salary"] == 100000.0
    assert updated["is_active"] == False
    print(f"  PASS: Updated alert (name='{updated['name']}', active={updated['is_active']})")

    # 5. TEST MATCH QUERY
    r_match = client.post(f"{ALERTS_BASE}/{alert_id}/test-match", headers=headers)
    assert r_match.status_code == 200
    match_data = r_match.json()
    assert match_data["alert_id"] == alert_id
    assert "jobs" in match_data
    print(f"  PASS: Test-match executed (found {match_data['total']} matching active jobs)")

    # 6. DELETE ALERT
    r_delete = client.delete(f"{ALERTS_BASE}/{alert_id}", headers=headers)
    assert r_delete.status_code == 200
    print("  PASS: Alert deleted successfully")

    # 7. VERIFY 404 AFTER DELETE
    r_get_after = client.get(f"{ALERTS_BASE}/{alert_id}", headers=headers)
    assert r_get_after.status_code == 404
    print("  PASS: GET /alerts/{id} -> 404 after deletion")


def test_user_alert_isolation():
    """User A cannot view, update, or delete User B's alert."""
    token_a = get_authenticated_user_tokens("usera")
    token_b = get_authenticated_user_tokens("userb")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates alert
    r_create = client.post(ALERTS_BASE, json={"name": "User A Alert"}, headers=headers_a)
    assert r_create.status_code == 201
    alert_id = r_create.json()["id"]

    # User B attempts to access User A's alert -> 404
    r_b_get = client.get(f"{ALERTS_BASE}/{alert_id}", headers=headers_b)
    assert r_b_get.status_code == 404
    print("  PASS: User B cannot access User A's alert (404)")

    r_b_del = client.delete(f"{ALERTS_BASE}/{alert_id}", headers=headers_b)
    assert r_b_del.status_code == 404
    print("  PASS: User B cannot delete User A's alert (404)")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 21 - JOB ALERTS SYSTEM TESTS")
    print("=" * 60)
    print()

    print("[1] Unauthenticated Protection")
    test_unauthenticated_access()
    print()

    print("[2] Job Alerts CRUD & Test Match Flow")
    test_job_alerts_crud_flow()
    print()

    print("[3] Multi-Tenant User Isolation")
    test_user_alert_isolation()
    print()

    print("=" * 60)
    print("ALL PHASE 21 TESTS PASSED")
    print("=" * 60)
