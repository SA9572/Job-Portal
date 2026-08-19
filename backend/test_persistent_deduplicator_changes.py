from datetime import datetime, timezone

from app.database.config import SessionLocal
from app.database.job_change_repository import (
    JobChangeRepository,
)
from app.database.job_repository import (
    JobRepository,
)
from app.models.job import Job
from app.services.persistent_deduplicator import (
    PersistentJobDeduplicator,
)


def create_job(
    title: str,
    content_hash: str,
) -> Job:

    now = datetime.now(
        timezone.utc
    )

    return Job(
        source="change-history-test",

        external_id=(
            "change-history-job-001"
        ),

        title=title,

        excerpt="Change history test",

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

        categories=["Testing"],

        parent_categories=["Testing"],

        description=(
            "Testing persistent job "
            "change history."
        ),

        published_at=now,

        expires_at=None,

        application_url=(
            "https://example.com/"
            "change-history-test"
        ),

        source_url=(
            "https://example.com/"
            "change-history-test"
        ),

        content_hash=content_hash,

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

    deduplicator = (
        PersistentJobDeduplicator(
            repository=job_repository,
            change_repository=change_repository,
        )
    )

    print(
        "========== PERSISTENT CHANGE HISTORY TEST =========="
    )

    # =========================================
    # FIRST VERSION
    # =========================================

    first_job = create_job(
        title="Machine Learning Engineer",
        content_hash="hash-version-001",
    )

    first_result = deduplicator.check(
        first_job
    )

    print()
    print(
        "========== FIRST VERSION =========="
    )

    print(
        "Result:",
        first_result,
    )

    # =========================================
    # SAME VERSION
    # =========================================

    duplicate_job = create_job(
        title="Machine Learning Engineer",
        content_hash="hash-version-001",
    )

    duplicate_result = (
        deduplicator.check(
            duplicate_job
        )
    )

    print()
    print(
        "========== DUPLICATE VERSION =========="
    )

    print(
        "Result:",
        duplicate_result,
    )

    # =========================================
    # CHANGED VERSION
    # =========================================

    changed_job = create_job(
        title=(
            "Senior Machine Learning Engineer"
        ),
        content_hash="hash-version-002",
    )

    changed_result = (
        deduplicator.check(
            changed_job
        )
    )

    print()
    print(
        "========== CHANGED VERSION =========="
    )

    print(
        "Result:",
        changed_result,
    )

    # =========================================
    # FIND DATABASE JOB
    # =========================================

    saved_job = (
        job_repository.get_by_identity(
            source="change-history-test",
            external_id=(
                "change-history-job-001"
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
        "Current title:",
        saved_job.title,
    )

    print(
        "Current hash:",
        saved_job.content_hash,
    )

    # =========================================
    # FIND CHANGE HISTORY
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

        print(
            "Source:",
            change.source,
        )

        print(
            "External ID:",
            change.external_id,
        )

finally:

    session.close()