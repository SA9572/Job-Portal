from fastapi.testclient import TestClient

from app.api.main import app
from app.database.config import SessionLocal
from app.database.job_repository import JobRepository


print("========== FILTER METADATA TEST ==========")

# =========================================
# TEST 1: REPOSITORY METHOD DIRECTLY
# =========================================

print()
print("========== TEST 1: REPOSITORY METHOD ==========")

session = SessionLocal()

try:

    repository = JobRepository(session)

    filters = repository.get_filter_options()

    print("Companies count:", len(filters["companies"]))
    print("Employment types count:", len(filters["employment_types"]))
    print("Locations count:", len(filters["locations"]))
    print("Seniorities count:", len(filters["seniorities"]))
    print("Categories count:", len(filters["categories"]))
    print("Currencies count:", len(filters["currencies"]))
    print("Min salary:", filters["min_salary"])
    print("Max salary:", filters["max_salary"])

    assert isinstance(filters["companies"], list)
    assert isinstance(filters["employment_types"], list)
    assert isinstance(filters["locations"], list)
    assert isinstance(filters["seniorities"], list)
    assert isinstance(filters["categories"], list)
    assert isinstance(filters["currencies"], list)

    if filters["companies"]:
        print("Sample companies:", filters["companies"][:3])
    if filters["locations"]:
        print("Sample locations:", filters["locations"][:3])
    if filters["seniorities"]:
        print("Sample seniorities:", filters["seniorities"])
    if filters["categories"]:
        print("Sample categories:", filters["categories"][:3])

finally:

    session.close()

# =========================================
# TEST 2: GET /api/jobs/filters API
# =========================================

print()
print("========== TEST 2: GET /api/jobs/filters API ==========")

client = TestClient(app)

response = client.get("/api/jobs/filters")

print("Status:", response.status_code)

data = response.json()

print("Keys returned:", list(data.keys()))

assert response.status_code == 200
assert "companies" in data
assert "employment_types" in data
assert "locations" in data
assert "seniorities" in data
assert "categories" in data
assert "currencies" in data
assert "min_salary" in data
assert "max_salary" in data

print()
print("========== FILTER METADATA TEST COMPLETED ==========")
