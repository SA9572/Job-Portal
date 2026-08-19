from datetime import datetime

from pydantic import BaseModel


# =============================================
# JOB RESPONSE
#
# Public API response for a single job.
# Matches the existing JSON structure.
# =============================================

class JobResponse(BaseModel):

    id: int

    source: str

    external_id: str

    title: str

    excerpt: str | None = None

    company: str

    company_slug: str | None = None

    company_logo: str | None = None

    employment_type: str | None = None

    minimum_salary: float | None = None

    maximum_salary: float | None = None

    salary_period: str | None = None

    currency: str | None = None

    seniority: list = []

    location_restrictions: list = []

    timezone_restrictions: list = []

    categories: list = []

    parent_categories: list = []

    description: str

    published_at: datetime | None = None

    expires_at: datetime | None = None

    application_url: str

    source_url: str

    content_hash: str

    fetched_at: datetime

    created_at: datetime

    updated_at: datetime

    is_deleted: bool = False

    deleted_at: datetime | None = None

    fts_snippet: str | None = None

    relevance_score: float | None = None

    model_config = {
        "from_attributes": True,
    }


# =============================================
# PAGINATION METADATA
# =============================================

class PaginationMetadata(BaseModel):

    count: int

    total: int

    limit: int

    offset: int


# =============================================
# JOB LIST RESPONSE
# =============================================

class JobListResponse(BaseModel):

    count: int

    total: int

    limit: int

    offset: int

    jobs: list[JobResponse]


# =============================================
# FILTER OPTIONS RESPONSE
# =============================================

class FilterOptionsResponse(BaseModel):

    companies: list[str]

    employment_types: list[str]

    locations: list[str]

    seniorities: list[str]

    categories: list[str]

    currencies: list[str]

    min_salary: float | None = None

    max_salary: float | None = None


# =============================================
# JOB CHANGE RESPONSE
# =============================================

class JobChangeResponse(BaseModel):

    id: int

    job_id: int

    source: str

    external_id: str

    old_content_hash: str

    new_content_hash: str

    changed_at: datetime

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


# =============================================
# JOB CHANGE LIST RESPONSE
# =============================================

class JobChangeListResponse(BaseModel):

    count: int

    total: int

    limit: int

    offset: int

    changes: list[JobChangeResponse]


# =============================================
# INGESTION RUN RESPONSE
# =============================================

class IngestionRunResponse(BaseModel):

    id: int

    source: str

    started_at: datetime

    finished_at: datetime | None = None

    pages_attempted: int

    pages_succeeded: int

    pages_failed: int

    jobs_fetched: int

    jobs_valid: int

    jobs_invalid: int

    jobs_new: int

    jobs_duplicate: int

    jobs_changed: int

    status: str

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


# =============================================
# INGESTION RUN LIST RESPONSE
# =============================================

class IngestionRunListResponse(BaseModel):

    count: int

    total: int

    limit: int

    offset: int

    runs: list[IngestionRunResponse]


# =============================================
# INGESTION ERROR RESPONSE
# =============================================

class IngestionErrorResponse(BaseModel):

    id: int

    ingestion_run_id: int

    source: str

    page_number: int

    offset: int

    status_code: int | None = None

    attempts: int

    error_type: str

    message: str

    occurred_at: datetime

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


# =============================================
# INGESTION ERROR LIST RESPONSE
# =============================================

class IngestionErrorListResponse(BaseModel):

    count: int

    total: int

    limit: int

    offset: int

    errors: list[IngestionErrorResponse]


# =============================================
# INGESTION TRIGGER REQUEST & RESPONSE
# =============================================

class IngestionTriggerRequest(BaseModel):

    max_pages: int = 5

    page_size: int = 20


class IngestionTriggerResponse(BaseModel):

    message: str

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

    errors_count: int


# =============================================
# JOB STATS RESPONSE
# =============================================

class JobStatsResponse(BaseModel):

    total: int

    active: int

    expired: int

    deleted: int


# =============================================
# SIMILAR JOB RESPONSE
# =============================================

class SimilarJobResponse(JobResponse):

    similarity_score: float


# =============================================
# SIMILAR JOB LIST RESPONSE
# =============================================

class SimilarJobListResponse(BaseModel):

    count: int

    total: int

    limit: int

    offset: int

    jobs: list[SimilarJobResponse]

