from sqlalchemy import inspect

from app.database.config import engine
from app.database.job_model import JobModel
from migrations.env import target_metadata


print("========== DATABASE INDEXES & QUALITY TEST ==========")

# =========================================
# TEST 1: INSPECT JOBS TABLE INDEXES
# =========================================

print()
print("========== TEST 1: INSPECT JOBS TABLE INDEXES ==========")

inspector = inspect(engine)

indexes = inspector.get_indexes("jobs")

index_names = {idx["name"] for idx in indexes}

print("Found indexes on 'jobs' table:")
for idx in sorted(index_names):
    print(f"- {idx}")

expected_indexes = {
    "ix_jobs_published_at",
    "ix_jobs_company",
    "ix_jobs_employment_type",
    "ix_jobs_minimum_salary",
    "ix_jobs_maximum_salary",
    "ix_jobs_created_at",
    "ix_jobs_source",
}

for exp in expected_indexes:
    assert exp in index_names, f"Missing index: {exp}"

print("All 7 performance indexes verified on 'jobs' table.")

# =========================================
# TEST 2: ALEMBIC TARGET METADATA
# =========================================

print()
print("========== TEST 2: ALEMBIC TARGET METADATA ==========")

print("Alembic target_metadata tables:")
for tbl in target_metadata.tables.keys():
    print(f"- {tbl}")

assert "jobs" in target_metadata.tables
assert "ingestion_runs" in target_metadata.tables
assert "ingestion_errors" in target_metadata.tables
assert "job_changes" in target_metadata.tables

print()
print("========== DATABASE INDEXES & QUALITY TEST COMPLETED ==========")
