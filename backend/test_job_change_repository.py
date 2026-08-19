from datetime import datetime, timezone

from app.database.config import SessionLocal
from app.database.job_change_repository import (
    JobChangeRepository,
)
from app.database.job_repository import (
    JobRepository,
)
from app.models.job import Job


def create_test_job():

    now = datetime.now(
        timezone.utc
    )

    return Job(
        source="change-repository-test",

        external_id=(
            "change-repository-job-001"
        ),

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

        categories=[
            "Machine Learning"
        ],

        parent_categories=[
            "Engineering"
        ],

        description=(
            "Repository change history test."
        ),

        published_at=now,

        expires_at=None,

        application_url=(
            "https://example.com/"
            "change-repository"
        ),

        source_url=(
            "https://example.com/"
            "change-repository"
        ),

        content_hash="hash-original",

        fetched_at=now,
    )


session = SessionLocal()

try:

    job_repository = JobRepository(
        session
    )

    change_repository = (
        JobChangeRepository(
            session
        )
    )

    print(
        "========== JOB CHANGE REPOSITORY TEST =========="
    )

    # -----------------------------------------
    # CREATE JOB
    # -----------------------------------------

    job = create_test_job()

    saved_job = job_repository.create(
        job
    )

    print(
        "Created job ID:",
        saved_job.id,
    )

    # -----------------------------------------
    # CREATE CHANGE
    # -----------------------------------------

    change = change_repository.create(

        job_id=saved_job.id,

        source=saved_job.source,

        external_id=saved_job.external_id,

        old_content_hash="hash-original",

        new_content_hash="hash-updated",
    )

    print()
    print(
        "========== CREATE TEST =========="
    )

    print(
        "Change ID:",
        change.id,
    )

    print(
        "Job ID:",
        change.job_id,
    )

    print(
        "Old hash:",
        change.old_content_hash,
    )

    print(
        "New hash:",
        change.new_content_hash,
    )

    # -----------------------------------------
    # READ BY JOB ID
    # -----------------------------------------

    changes = (
        change_repository.get_by_job_id(
            saved_job.id
        )
    )

    print()
    print(
        "========== READ BY JOB ID =========="
    )

    print(
        "Changes found:",
        len(changes),
    )

    if changes:

        first_change = changes[0]

        print(
            "First old hash:",
            first_change.old_content_hash,
        )

        print(
            "First new hash:",
            first_change.new_content_hash,
        )

    # -----------------------------------------
    # READ BY EXTERNAL ID
    # -----------------------------------------

    changes_by_external_id = (
        change_repository.get_by_external_id(

            source=saved_job.source,

            external_id=(
                saved_job.external_id
            ),
        )
    )

    print()
    print(
        "========== READ BY EXTERNAL ID =========="
    )

    print(
        "Changes found:",
        len(
            changes_by_external_id
        ),
    )

finally:

    session.close()