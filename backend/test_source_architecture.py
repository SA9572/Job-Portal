from unittest.mock import MagicMock
import pytest

from app.models.job import Job
from app.services.ingestion_service import IngestionService
from app.sources.base import JobSource
from app.sources.himalayas import HimalayasSource
from app.sources.remoteok import RemoteOKSource


print("========== SOURCE ARCHITECTURE TEST ==========")

# =========================================
# TEST 1: JOBSOURCE ABSTRACT BASE CLASS
# =========================================

print()
print("========== TEST 1: JOBSOURCE ABSTRACT CLASS ==========")

try:
    source = JobSource()
    assert False, "JobSource ABC should not be instantiable"
except TypeError:
    print("JobSource ABC correctly enforces non-instantiability of abstract class.")

# =========================================
# TEST 2: HIMALAYAS SOURCE IMPLEMENTATION
# =========================================

print()
print("========== TEST 2: HIMALAYAS SOURCE ==========")

h_source = HimalayasSource()
assert issubclass(HimalayasSource, JobSource)
assert h_source.source_name == "himalayas"
print("HimalayasSource implements JobSource correctly. source_name:", h_source.source_name)

# =========================================
# TEST 3: REMOTEOK SOURCE IMPLEMENTATION
# =========================================

print()
print("========== TEST 3: REMOTEOK SOURCE ==========")

mock_http = MagicMock()
mock_http.get.return_value.json.return_value = [
    {"legal": "Notice"},
    {
        "id": "12345",
        "position": "Senior Python Engineer",
        "company": "Tech Corp",
        "description": "Great job opportunity for Python devs.",
        "url": "https://remoteok.com/job-12345",
        "salary_min": 120000,
        "salary_max": 150000,
        "tags": ["python", "backend"],
        "location": "Worldwide",
    },
]

r_source = RemoteOKSource(http_client=mock_http)
assert issubclass(RemoteOKSource, JobSource)
assert r_source.source_name == "remoteok"

jobs = r_source.fetch_jobs(limit=10, offset=0)
assert len(jobs) == 1
j = jobs[0]
assert j.source == "remoteok"
assert j.external_id == "12345"
assert j.title == "Senior Python Engineer"
assert j.company == "Tech Corp"
assert j.minimum_salary == 120000.0

print("RemoteOKSource implements JobSource correctly and normalizes raw jobs.")

# =========================================
# TEST 4: INGESTION SERVICE MULTI-SOURCE SUPPORT
# =========================================

print()
print("========== TEST 4: INGESTION SERVICE WITH REMOTEOK SOURCE ==========")

service = IngestionService(source=r_source)
result = service.run(max_pages=1, page_size=10)

print("Ingestion result source:", result.source)
print("Jobs fetched:", result.jobs_fetched)
print("Jobs valid:", result.jobs_valid)

assert result.source == "remoteok"
assert result.jobs_fetched == 1
assert result.jobs_valid == 1

print()
print("========== SOURCE ARCHITECTURE TEST COMPLETED ==========")
