from datetime import datetime
from pydantic import BaseModel, HttpUrl


class Job(BaseModel):
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

    seniority: list[str] = []
    location_restrictions: list[str] = []
    timezone_restrictions: list[float] = []

    categories: list[str] = []
    parent_categories: list[str] = []

    description: str

    published_at: datetime | None = None
    expires_at: datetime | None = None

    application_url: HttpUrl
    source_url: HttpUrl

    content_hash: str | None = None
    fetched_at: datetime