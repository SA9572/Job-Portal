from fastapi.testclient import TestClient

from app.api.main import app


print("========== API ERROR HANDLING TEST ==========")

client = TestClient(app)

# =========================================
# TEST 1: 404 NOT FOUND ERROR STRUCTURE
# =========================================

print()
print("========== TEST 1: 404 NOT FOUND ==========")

response = client.get("/api/jobs/9999999")

print("Status:", response.status_code)

body = response.json()

print("Response body:", body)

assert response.status_code == 404
assert "error" in body
err = body["error"]
assert err["code"] == "NOT_FOUND"
assert err["message"] == "Job not found"
assert err["status_code"] == 404
assert "timestamp" in err

# =========================================
# TEST 2: 400 BAD REQUEST ERROR STRUCTURE
# =========================================

print()
print("========== TEST 2: 400 BAD REQUEST ==========")

response = client.get("/api/jobs?sort_by=invalid_column_name")

print("Status:", response.status_code)

body = response.json()

print("Response body:", body)

assert response.status_code == 400
assert "error" in body
err = body["error"]
assert err["code"] == "BAD_REQUEST"
assert err["status_code"] == 400
assert "timestamp" in err

# =========================================
# TEST 3: 422 UNPROCESSABLE ENTITY STRUCTURE
# =========================================

print()
print("========== TEST 3: 422 VALIDATION ERROR ==========")

response = client.get("/api/jobs/string_instead_of_int")

print("Status:", response.status_code)

body = response.json()

print("Response body:", body)

assert response.status_code == 422
assert "error" in body
err = body["error"]
assert err["code"] == "UNPROCESSABLE_ENTITY"
assert err["status_code"] == 422
assert "details" in err

print()
print("========== API ERROR HANDLING TEST COMPLETED ==========")
