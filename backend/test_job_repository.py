from datetime import datetime, timezone

from app.database.config import SessionLocal
from app.database.job_repository import JobRepository
from app.models.job import Job


def create_test_job(
    external_id: str,
    content_hash: str,
):

    return Job(
        source="repository-test",
        external_id=external_id,

        title="Machine Learning Engineer",
        excerpt="Repository test job",

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

        description=(
            "Repository test job."
        ),

        published_at=datetime.now(
            timezone.utc
        ),

        expires_at=None,

        application_url=(
            "https://example.com/repository-test"
        ),

        source_url=(
            "https://example.com/repository-test"
        ),

        content_hash=content_hash,

        fetched_at=datetime.now(
            timezone.utc
        ),
    )


session = SessionLocal()

try:

    repository = JobRepository(session)

    print(
        "========== REPOSITORY TEST =========="
    )

    # ---------------------------------
    # CREATE
    # ---------------------------------

    job = create_test_job(
        external_id="repository-job-001",
        content_hash="hash-001",
    )

    created = repository.create(job)

    print(
        "Created ID:",
        created.id,
    )

    # ---------------------------------
    # READ
    # ---------------------------------

    found = repository.get_by_identity(
        source="repository-test",
        external_id="repository-job-001",
    )

    print(
        "Found:",
        found is not None,
    )

    print(
        "Found title:",
        found.title if found else None,
    )

    # ---------------------------------
    # UPDATE
    # ---------------------------------

    updated_job = create_test_job(
        external_id="repository-job-001",
        content_hash="hash-002",
    )

    updated_job.title = (
        "Senior Machine Learning Engineer"
    )

    updated = repository.update(
        found,
        updated_job,
    )

    print(
        "Updated title:",
        updated.title,
    )

    print(
        "Updated hash:",
        updated.content_hash,
    )

    # ---------------------------------
    # VERIFY UPDATE
    # ---------------------------------

    verified = repository.get_by_identity(
        source="repository-test",
        external_id="repository-job-001",
    )

    print(
        "Verified title:",
        verified.title,
    )

    print(
        "Verified hash:",
        verified.content_hash,
    )

finally:

    session.close()