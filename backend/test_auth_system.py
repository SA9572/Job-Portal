"""
Phase 19 — User Authentication & JWT Security System Tests

Tests the complete Phase 19 implementation:
1. User registration (POST /api/auth/register)
2. Duplicate email registration rejection (400)
3. Valid & invalid login (POST /api/auth/login)
4. Authenticated profile endpoint (GET /api/auth/me) with valid Bearer token
5. Unauthorized access (401) on /me with missing or invalid token
6. Refresh token flow (POST /api/auth/refresh)
7. Default Admin user login & admin role validation
"""

from fastapi.testclient import TestClient
from app.api.main import app

import time

client = TestClient(app)
AUTH_BASE = "/api/auth"

UNIQUE_EMAIL = f"testuser_{int(time.time())}@example.com"


def test_user_registration():
    """Test POST /api/auth/register creates user and returns JWT tokens."""
    payload = {
        "email": UNIQUE_EMAIL,
        "password": "UserPass123!",
        "full_name": "Test User",
    }
    r = client.post(f"{AUTH_BASE}/register", json=payload)
    assert r.status_code == 201, f"Registration failed: {r.status_code} {r.text}"
    data = r.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data

    user = data["user"]
    assert user["email"] == UNIQUE_EMAIL
    assert user["full_name"] == "Test User"
    assert user["role"] == "user"
    assert user["is_active"] == True
    print(f"  PASS: User registration successful (id={user['id']}, email='{user['email']}')")
    return data


def test_duplicate_registration_rejected():
    """Test duplicate email registration returns 400."""
    payload = {
        "email": UNIQUE_EMAIL,
        "password": "AnotherPassword123!",
    }
    r = client.post(f"{AUTH_BASE}/register", json=payload)
    assert r.status_code == 400
    print("  PASS: Duplicate email registration correctly rejected (400)")


def test_user_login():
    """Test POST /api/auth/login with valid and invalid credentials."""
    # Invalid password
    r_bad = client.post(
        f"{AUTH_BASE}/login",
        json={"email": UNIQUE_EMAIL, "password": "WrongPassword"},
    )
    assert r_bad.status_code == 401
    print("  PASS: Invalid password login rejected (401)")

    # Nonexistent user
    r_no_user = client.post(
        f"{AUTH_BASE}/login",
        json={"email": "nobody@example.com", "password": "UserPass123!"},
    )
    assert r_no_user.status_code == 401
    print("  PASS: Nonexistent email login rejected (401)")

    # Valid login
    r_good = client.post(
        f"{AUTH_BASE}/login",
        json={"email": UNIQUE_EMAIL, "password": "UserPass123!"},
    )
    assert r_good.status_code == 200
    data = r_good.json()
    assert "access_token" in data
    assert "refresh_token" in data
    print("  PASS: Valid login returned access & refresh tokens")
    return data["access_token"], data["refresh_token"]


def test_auth_me_endpoint(access_token: str):
    """Test GET /api/auth/me returns current user profile."""
    # Missing token -> 401
    r_unauth = client.get(f"{AUTH_BASE}/me")
    assert r_unauth.status_code == 401
    print("  PASS: GET /me without token returned 401")

    # Invalid token -> 401
    r_invalid = client.get(
        f"{AUTH_BASE}/me",
        headers={"Authorization": "Bearer invalid_token_xyz"},
    )
    assert r_invalid.status_code == 401
    print("  PASS: GET /me with invalid token returned 401")

    # Valid token -> 200
    r_me = client.get(
        f"{AUTH_BASE}/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert r_me.status_code == 200
    user = r_me.json()
    assert user["email"] == UNIQUE_EMAIL
    print(f"  PASS: GET /me with valid token returned profile (email='{user['email']}')")


def test_token_refresh(refresh_token: str):
    """Test POST /api/auth/refresh returns new token pair."""
    # Invalid refresh token -> 401
    r_bad = client.post(f"{AUTH_BASE}/refresh", json={"refresh_token": "invalid_refresh"})
    assert r_bad.status_code == 401
    print("  PASS: Invalid refresh token rejected (401)")

    # Valid refresh token -> 200
    r_good = client.post(f"{AUTH_BASE}/refresh", json={"refresh_token": refresh_token})
    assert r_good.status_code == 200
    data = r_good.json()
    assert "access_token" in data
    assert "refresh_token" in data
    print("  PASS: Token refresh generated new access & refresh tokens")


def test_admin_login():
    """Test default seeded admin user login."""
    r = client.post(
        f"{AUTH_BASE}/login",
        json={"email": "admin@jobrequired.com", "password": "AdminPass123!"},
    )
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    data = r.json()
    assert data["user"]["role"] == "admin"
    print(f"  PASS: Seeded admin login successful (role='{data['user']['role']}')")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 19 - USER AUTHENTICATION & JWT SECURITY TESTS")
    print("=" * 60)
    print()

    print("[1] User Registration")
    test_user_registration()
    print()

    print("[2] Duplicate Registration Prevention")
    test_duplicate_registration_rejected()
    print()

    print("[3] User Login")
    access_token, refresh_token = test_user_login()
    print()

    print("[4] Authenticated GET /me Profile")
    test_auth_me_endpoint(access_token)
    print()

    print("[5] Token Refresh Flow")
    test_token_refresh(refresh_token)
    print()

    print("[6] Admin Login & Role Check")
    test_admin_login()
    print()

    print("=" * 60)
    print("ALL PHASE 19 TESTS PASSED")
    print("=" * 60)
