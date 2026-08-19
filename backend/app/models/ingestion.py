from datetime import datetime

from pydantic import BaseModel


class IngestionError(BaseModel):
    source: str
    page_number: int | None = None
    offset: int | None = None
    status_code: int | None = None
    attempts: int
    error_type: str
    message: str
    occurred_at: datetime


class IngestionResult(BaseModel):
    source: str
    pages_attempted: int
    pages_succeeded: int
    pages_failed: int
    jobs_fetched: int
    jobs_valid: int
    jobs_invalid: int
    jobs_new: int
    jobs_duplicate: int
    jobs_changed: int
    errors: list[IngestionError] = []