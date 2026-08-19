from app.database.config import SessionLocal
from app.database.ingestion_error_model import (
    IngestionErrorModel,
)
from app.database.ingestion_error_repository import (
    IngestionErrorRepository,
)
from app.database.ingestion_run_model import (
    IngestionRunModel,
)
from app.database.ingestion_run_repository import (
    IngestionRunRepository,
)
from app.database.job_repository import (
    JobRepository,
)
from app.models.job import Job
from app.services.http_client import (
    HttpRequestError,
)
from app.services.ingestion_service import (
    IngestionService,
)
from app.services.persistent_deduplicator import (
    PersistentJobDeduplicator,
)


class FakeSource:

    def __init__(self):
        self.calls = 0

    def fetch_jobs(
        self,
        limit: int = 20,
        offset: int = 0,
    ):

        self.calls += 1

        # Page 2 fails
        if self.calls == 2:

            raise HttpRequestError(
                message=(
                    "Retryable HTTP status: 503"
                ),
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
        source="error-integration-test",

        external_id=(
            f"error-job-{index}"
        ),

        title=(
            f"Test Job {index}"
        ),

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
            "Valid test job description."
        ),

        published_at=None,

        expires_at=None,

        application_url=(
            f"https://example.com/jobs/{index}"
        ),

        source_url=(
            f"https://example.com/jobs/{index}"
        ),

        content_hash=(
            f"error-hash-{index}"
        ),

        fetched_at=__import__(
            "datetime"
        ).datetime.now(
            __import__(
                "datetime"
            ).timezone.utc
        ),
    )


class FakeValidator:

    def validate(self, job):

        return []


session = SessionLocal()

try:

    job_repository = JobRepository(
        session
    )

    run_repository = (
        IngestionRunRepository(
            session
        )
    )

    error_repository = (
        IngestionErrorRepository(
            session
        )
    )

    deduplicator = (
        PersistentJobDeduplicator(
            job_repository
        )
    )

    service = IngestionService(

        source=FakeSource(),

        validator=FakeValidator(),

        deduplicator=deduplicator,

        ingestion_run_repository=(
            run_repository
        ),

        ingestion_error_repository=(
            error_repository
        ),
    )

    print(
        "========== ERROR INTEGRATION TEST =========="
    )

    result = service.run(
        max_pages=3,
        page_size=20,
    )

    print()
    print(
        "========== INGESTION RESULT =========="
    )

    print(
        "Pages attempted:",
        result.pages_attempted,
    )

    print(
        "Pages succeeded:",
        result.pages_succeeded,
    )

    print(
        "Pages failed:",
        result.pages_failed,
    )

    print(
        "Jobs fetched:",
        result.jobs_fetched,
    )

    print(
        "Errors:",
        len(result.errors),
    )

    # =========================================
    # FIND LATEST RUN
    # =========================================

    run = (
        session.query(
            IngestionRunModel
        )
        .filter(
            IngestionRunModel.source
            == "himalayas"
        )
        .order_by(
            IngestionRunModel.id.desc()
        )
        .first()
    )

    print()
    print(
        "========== DATABASE RUN =========="
    )

    print(
        "Run ID:",
        run.id if run else None,
    )

    print(
        "Status:",
        run.status if run else None,
    )

    print(
        "Pages failed:",
        run.pages_failed if run else None,
    )

    # =========================================
    # FIND ERRORS FOR RUN
    # =========================================

    if run:

        saved_errors = (
            error_repository.get_by_run_id(
                run.id
            )
        )

    else:

        saved_errors = []

    print()
    print(
        "========== DATABASE ERRORS =========="
    )

    print(
        "Errors saved:",
        len(saved_errors),
    )

    for error in saved_errors:

        print(
            "Page:",
            error.page_number,
        )

        print(
            "Offset:",
            error.offset,
        )

        print(
            "Status:",
            error.status_code,
        )

        print(
            "Attempts:",
            error.attempts,
        )

        print(
            "Type:",
            error.error_type,
        )

        print(
            "Message:",
            error.message,
        )

finally:

    session.close()