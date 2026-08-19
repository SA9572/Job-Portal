from datetime import datetime, timezone

from app.database.config import SessionLocal
from app.database.job_repository import JobRepository
from app.models.job import Job
from app.services.persistent_deduplicator import (
    PersistentJobDeduplicator,
)


def create_job(
    external_id: str,
    content_hash: str,
    title: str = "Machine Learning Engineer",
):

    return Job(
        source="persistent-test",
        external_id=external_id,

        title=title,
        excerpt="Test job",

        company="Test Company",
        company_slug="test-company",
        company_logo=None,

        employment_type="Full Time",

        minimum_salary=100000,
        maximum_salary=150000,
        salary_period="annual",
        currency="USD",

        seniority=["Junior"],

        location_restrictions=["India"],
        timezone_restrictions=[5.5],

        categories=["Machine Learning"],
        parent_categories=["Engineering"],

        description="Persistent deduplication test.",

        published_at=datetime.now(
            timezone.utc
        ),

        expires_at=None,

        application_url=(
            "https://example.com/persistent-test"
        ),

        source_url=(
            "https://example.com/persistent-test"
        ),

        content_hash=content_hash,

        fetched_at=datetime.now(
            timezone.utc
        ),
    )


session = SessionLocal()

try:

    repository = JobRepository(session)

    deduplicator = (
        PersistentJobDeduplicator(
            repository
        )
    )

    print(
        "========== PERSISTENT DEDUPLICATION TEST =========="
    )

    # ---------------------------------
    # FIRST INSERT
    # ---------------------------------

    job_1 = create_job(
        external_id="persistent-job-001",
        content_hash="hash-001",
    )

    result_1 = deduplicator.check(job_1)

    print(
        "First check:",
        result_1,
    )

    # ---------------------------------
    # SAME JOB
    # ---------------------------------

    job_2 = create_job(
        external_id="persistent-job-001",
        content_hash="hash-001",
    )

    result_2 = deduplicator.check(job_2)

    print(
        "Second check:",
        result_2,
    )

    # ---------------------------------
    # CHANGED JOB
    # ---------------------------------

    job_3 = create_job(
        external_id="persistent-job-001",
        content_hash="hash-002",
        title="Senior Machine Learning Engineer",
    )

    result_3 = deduplicator.check(job_3)

    print(
        "Changed job check:",
        result_3,
    )

    # ---------------------------------
    # VERIFY DATABASE
    # ---------------------------------

    saved = repository.get_by_identity(
        source="persistent-test",
        external_id="persistent-job-001",
    )

    print()
    print(
        "========== DATABASE VERIFICATION =========="
    )

    print(
        "Saved title:",
        saved.title,
    )

    print(
        "Saved hash:",
        saved.content_hash,
    )

finally:

    session.close()