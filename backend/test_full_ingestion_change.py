from app.database.config import SessionLocal
from app.database.job_change_repository import (
    JobChangeRepository,
)
from app.database.job_repository import (
    JobRepository,
)
from app.database.ingestion_run_repository import (
    IngestionRunRepository,
)
from app.database.ingestion_error_repository import (
    IngestionErrorRepository,
)
from app.services.ingestion_service import (
    IngestionService,
)
from app.services.persistent_deduplicator import (
    PersistentJobDeduplicator,
)
from app.services.validator import JobValidator
from app.models.job import Job

from datetime import datetime, timezone


class FakeSource:

    def __init__(self):

        self.calls = 0

    def fetch_jobs(
        self,
        limit=20,
        offset=0,
    ):

        self.calls += 1

        now = datetime.now(
            timezone.utc
        )

        # -----------------------------------------
        # FIRST INGESTION VERSION
        # -----------------------------------------

        if self.calls == 1:

            return [
                Job(
                    source="full-integration-test",

                    external_id="integration-job-001",

                    title="Machine Learning Engineer",

                    excerpt="Integration test",

                    company="Test Company",

                    company_slug="test-company",

                    company_logo=None,

                    employment_type="Full Time",

                    minimum_salary=None,

                    maximum_salary=None,

                    salary_period=None,

                    currency=None,

                    seniority=["Junior"],

                    location_restrictions=["India"],

                    timezone_restrictions=[5.5],

                    categories=["Machine Learning"],

                    parent_categories=["Engineering"],

                    description=(
                        "Original job description."
                    ),

                    published_at=now,

                    expires_at=None,

                    application_url=(
                        "https://example.com/"
                        "integration-job"
                    ),

                    source_url=(
                        "https://example.com/"
                        "integration-job"
                    ),

                    content_hash="integration-hash-001",

                    fetched_at=now,
                )
            ]

        # -----------------------------------------
        # SECOND INGESTION VERSION
        # -----------------------------------------

        return [
            Job(
                source="full-integration-test",

                external_id="integration-job-001",

                title=(
                    "Senior Machine Learning Engineer"
                ),

                excerpt="Integration test",

                company="Test Company",

                company_slug="test-company",

                company_logo=None,

                employment_type="Full Time",

                minimum_salary=None,

                maximum_salary=None,

                salary_period=None,

                currency=None,

                seniority=["Senior"],

                location_restrictions=["India"],

                timezone_restrictions=[5.5],

                categories=["Machine Learning"],

                parent_categories=["Engineering"],

                description=(
                    "Updated job description."
                ),

                published_at=now,

                expires_at=None,

                application_url=(
                    "https://example.com/"
                    "integration-job"
                ),

                source_url=(
                    "https://example.com/"
                    "integration-job"
                ),

                content_hash="integration-hash-002",

                fetched_at=now,
            )
        ]


session = SessionLocal()

try:

    # =========================================
    # CREATE REPOSITORIES
    # =========================================

    job_repository = JobRepository(
        session
    )

    change_repository = (
        JobChangeRepository(
            session
        )
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

    # =========================================
    # CREATE DEDUPLICATOR
    # =========================================

    deduplicator = (
        PersistentJobDeduplicator(

            repository=job_repository,

            change_repository=(
                change_repository
            ),
        )
    )

    # =========================================
    # CREATE SERVICE
    # =========================================

    source = FakeSource()

    service = IngestionService(

        source=source,

        validator=JobValidator(),

        deduplicator=deduplicator,

        ingestion_run_repository=(
            run_repository
        ),

        ingestion_error_repository=(
            error_repository
        ),
    )

    print(
        "========== FULL CHANGE INGESTION TEST =========="
    )

    # =========================================
    # FIRST RUN
    # =========================================

    first_result = service.run(
        max_pages=1,
        page_size=20,
    )

    print()
    print(
        "========== FIRST RUN =========="
    )

    print(
        "Jobs fetched:",
        first_result.jobs_fetched,
    )

    print(
        "Jobs new:",
        first_result.jobs_new,
    )

    print(
        "Jobs duplicate:",
        first_result.jobs_duplicate,
    )

    print(
        "Jobs changed:",
        first_result.jobs_changed,
    )

    # =========================================
    # SECOND RUN
    # =========================================

    second_result = service.run(
        max_pages=1,
        page_size=20,
    )

    print()
    print(
        "========== SECOND RUN =========="
    )

    print(
        "Jobs fetched:",
        second_result.jobs_fetched,
    )

    print(
        "Jobs new:",
        second_result.jobs_new,
    )

    print(
        "Jobs duplicate:",
        second_result.jobs_duplicate,
    )

    print(
        "Jobs changed:",
        second_result.jobs_changed,
    )

    # =========================================
    # READ CURRENT JOB
    # =========================================

    saved_job = (
        job_repository.get_by_identity(

            source=(
                "full-integration-test"
            ),

            external_id=(
                "integration-job-001"
            ),
        )
    )

    print()
    print(
        "========== CURRENT JOB =========="
    )

    print(
        "Job ID:",
        saved_job.id,
    )

    print(
        "Title:",
        saved_job.title,
    )

    print(
        "Current hash:",
        saved_job.content_hash,
    )

    # =========================================
    # READ CHANGE HISTORY
    # =========================================

    changes = (
        change_repository.get_by_job_id(
            saved_job.id
        )
    )

    print()
    print(
        "========== CHANGE HISTORY =========="
    )

    print(
        "Changes found:",
        len(changes),
    )

    for change in changes:

        print(
            "Change ID:",
            change.id,
        )

        print(
            "Old hash:",
            change.old_content_hash,
        )

        print(
            "New hash:",
            change.new_content_hash,
        )

finally:

    session.close()