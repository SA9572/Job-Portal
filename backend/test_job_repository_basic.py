from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from app.database.config import SessionLocal
from app.database.job_model import JobModel


def create_test_job():

    return JobModel(
        source="test",
        external_id="test-job-001",

        title="Test Machine Learning Engineer",
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

        description=(
            "Test job used to verify "
            "database persistence."
        ),

        published_at=datetime.now(timezone.utc),
        expires_at=None,

        application_url=(
            "https://example.com/jobs/test-job-001"
        ),

        source_url=(
            "https://example.com/jobs/test-job-001"
        ),

        content_hash="test-hash-001",

        fetched_at=datetime.now(timezone.utc),
    )


session = SessionLocal()

try:

    print(
        "========== INSERT TEST =========="
    )

    job = create_test_job()

    session.add(job)
    session.commit()
    session.refresh(job)

    print("Inserted job ID:", job.id)
    print("Title:", job.title)
    print("Company:", job.company)

    print()
    print(
        "========== READ TEST =========="
    )

    saved_job = (
        session.query(JobModel)
        .filter(
            JobModel.external_id
            == "test-job-001"
        )
        .first()
    )

    if saved_job:

        print("Job found: YES")
        print("Database ID:", saved_job.id)
        print("Title:", saved_job.title)
        print("Company:", saved_job.company)

    else:

        print("Job found: NO")

    print()
    print(
        "========== DUPLICATE TEST =========="
    )

    duplicate_job = create_test_job()

    session.add(duplicate_job)

    try:

        session.commit()

        print(
            "Duplicate accepted: FAILED"
        )

    except IntegrityError:

        session.rollback()

        print(
            "Duplicate blocked: SUCCESS"
        )

finally:

    session.close()