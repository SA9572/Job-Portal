from datetime import datetime, timezone

from app.models.ingestion import IngestionError


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


print("========== INGESTION ERROR ==========")

print("Source:", error.source)
print("Page:", error.page_number)
print("Offset:", error.offset)
print("Status:", error.status_code)
print("Attempts:", error.attempts)
print("Error Type:", error.error_type)
print("Message:", error.message)
print("Occurred At:", error.occurred_at)