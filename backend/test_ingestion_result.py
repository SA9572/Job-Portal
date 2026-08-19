from datetime import datetime, timezone

from app.models.ingestion import (
    IngestionError,
    IngestionResult,
)


error = IngestionError(
    source="himalayas",
    page_number=4,
    offset=60,
    status_code=503,
    attempts=3,
    error_type="HTTPStatusError",
    message="Service unavailable after retries",
    occurred_at=datetime.now(timezone.utc),
)


result = IngestionResult(
    source="himalayas",
    pages_attempted=5,
    pages_succeeded=4,
    pages_failed=1,
    jobs_fetched=80,
    jobs_valid=78,
    jobs_invalid=2,
    jobs_new=60,
    jobs_duplicate=15,
    jobs_changed=3,
    errors=[error],
)


print("========== INGESTION RESULT ==========")

print("Source:", result.source)
print("Pages attempted:", result.pages_attempted)
print("Pages succeeded:", result.pages_succeeded)
print("Pages failed:", result.pages_failed)

print("Jobs fetched:", result.jobs_fetched)
print("Jobs valid:", result.jobs_valid)
print("Jobs invalid:", result.jobs_invalid)

print("Jobs new:", result.jobs_new)
print("Jobs duplicate:", result.jobs_duplicate)
print("Jobs changed:", result.jobs_changed)

print("Errors:", len(result.errors))