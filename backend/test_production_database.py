from sqlalchemy import func

from app.database.config import SessionLocal
from app.database.job_model import JobModel
from app.database.job_change_model import JobChangeModel
from app.database.ingestion_run_model import IngestionRunModel
from app.database.ingestion_error_model import IngestionErrorModel


session = SessionLocal()

try:

    print("========== PRODUCTION DATABASE CHECK ==========")

    # -----------------------------------------
    # JOBS
    # -----------------------------------------

    job_count = (
        session.query(
            func.count(JobModel.id)
        ).scalar()
    )

    print()
    print("Jobs in database:", job_count)

    # -----------------------------------------
    # INGESTION RUNS
    # -----------------------------------------

    run_count = (
        session.query(
            func.count(IngestionRunModel.id)
        ).scalar()
    )

    print(
        "Ingestion runs:",
        run_count,
    )

    # -----------------------------------------
    # INGESTION ERRORS
    # -----------------------------------------

    error_count = (
        session.query(
            func.count(IngestionErrorModel.id)
        ).scalar()
    )

    print(
        "Ingestion errors:",
        error_count,
    )

    # -----------------------------------------
    # JOB CHANGES
    # -----------------------------------------

    change_count = (
        session.query(
            func.count(JobChangeModel.id)
        ).scalar()
    )

    print(
        "Job changes:",
        change_count,
    )

    # -----------------------------------------
    # LAST INGESTION RUN
    # -----------------------------------------

    latest_run = (
        session.query(
            IngestionRunModel
        )
        .order_by(
            IngestionRunModel.id.desc()
        )
        .first()
    )

    print()

    print(
        "========== LATEST INGESTION RUN =========="
    )

    if latest_run:

        print(
            "Run ID:",
            latest_run.id,
        )

        print(
            "Source:",
            latest_run.source,
        )

        print(
            "Status:",
            latest_run.status,
        )

        print(
            "Pages attempted:",
            latest_run.pages_attempted,
        )

        print(
            "Pages succeeded:",
            latest_run.pages_succeeded,
        )

        print(
            "Pages failed:",
            latest_run.pages_failed,
        )

        print(
            "Jobs fetched:",
            latest_run.jobs_fetched,
        )

        print(
            "Jobs new:",
            latest_run.jobs_new,
        )

        print(
            "Jobs duplicate:",
            latest_run.jobs_duplicate,
        )

        print(
            "Jobs changed:",
            latest_run.jobs_changed,
        )

        print(
            "Finished:",
            latest_run.finished_at is not None,
        )

    # -----------------------------------------
    # RECENT CHANGES
    # -----------------------------------------

    changes = (
        session.query(
            JobChangeModel
        )
        .order_by(
            JobChangeModel.id.desc()
        )
        .limit(10)
        .all()
    )

    print()

    print(
        "========== RECENT JOB CHANGES =========="
    )

    print(
        "Records displayed:",
        len(changes),
    )

    for change in changes:

        print(
            f"Change {change.id}: "
            f"{change.old_content_hash} "
            f"-> "
            f"{change.new_content_hash}"
        )

finally:

    session.close()