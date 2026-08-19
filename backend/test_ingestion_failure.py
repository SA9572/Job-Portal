from datetime import datetime, timezone

from app.models.job import Job
from app.services.ingestion_service import IngestionService
from app.services.http_client import HttpRequestError


class FakeSource:

    def __init__(self):
        self.calls = 0

    def fetch_jobs(
        self,
        limit: int = 20,
        offset: int = 0,
    ):

        self.calls += 1

        if self.calls == 2:

            raise HttpRequestError(
                message="Retryable HTTP status: 503",
                attempts=3,
                status_code=503,
            )

        return [
            create_fake_job(
                index=offset + i
            )
            for i in range(limit)
        ]


def create_fake_job(index: int):

    return Job(
        source="test",
        external_id=f"job-{index}",

        title=f"Test Job {index}",
        excerpt="Test job",

        company="Test Company",
        company_slug="test-company",
        company_logo=None,

        employment_type="Full Time",

        minimum_salary=None,
        maximum_salary=None,
        salary_period=None,
        currency=None,

        seniority=["Junior"],

        location_restrictions=[],
        timezone_restrictions=[],

        categories=["Testing"],
        parent_categories=["Testing"],

        description=(
            "This is a valid test job description "
            "used for ingestion testing."
        ),

        published_at=None,
        expires_at=None,

        application_url=(
            f"https://example.com/jobs/{index}"
        ),

        source_url=(
            f"https://example.com/jobs/{index}"
        ),

        content_hash=f"hash-{index}",

        fetched_at=datetime.now(timezone.utc),
    )


class FakeValidator:

    def validate(self, job):

        return []


class FakeDeduplicator:

    def check(self, job):

        return "new"


source = FakeSource()

service = IngestionService(
    source=source,
    validator=FakeValidator(),
    deduplicator=FakeDeduplicator(),
)


print("========== INGESTION FAILURE TEST ==========")

result = service.run(
    max_pages=3,
    page_size=20,
)


print()
print("========== RESULT ==========")

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


if result.errors:

    error = result.errors[0]

    print()
    print("========== FIRST ERROR ==========")

    print("Source:", error.source)
    print("Page:", error.page_number)
    print("Offset:", error.offset)
    print("Status:", error.status_code)
    print("Attempts:", error.attempts)
    print("Error Type:", error.error_type)
    print("Message:", error.message)