from app.database.config import SessionLocal
from app.database.ingestion_run_repository import (
    IngestionRunRepository,
)
from app.services.ingestion_service import (
    IngestionService,
)
from app.services.persistent_deduplicator import (
    PersistentJobDeduplicator,
)
from app.services.validator import JobValidator
from app.sources.himalayas import HimalayasSource


session = SessionLocal()

try:

    job_repository = (
        __import__(
            "app.database.job_repository",
            fromlist=["JobRepository"],
        ).JobRepository(session)
    )

    deduplicator = (
        PersistentJobDeduplicator(
            job_repository
        )
    )

    ingestion_run_repository = (
        IngestionRunRepository(
            session
        )
    )

    service = IngestionService(
        source=HimalayasSource(),
        validator=JobValidator(),
        deduplicator=deduplicator,
        ingestion_run_repository=(
            ingestion_run_repository
        ),
    )

    print(
        "========== INGESTION RUN INTEGRATION =========="
    )

    result = service.run(
        max_pages=1,
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
        "Jobs valid:",
        result.jobs_valid,
    )

    print(
        "Jobs invalid:",
        result.jobs_invalid,
    )

    print(
        "Jobs new:",
        result.jobs_new,
    )

    print(
        "Jobs duplicate:",
        result.jobs_duplicate,
    )

    print(
        "Jobs changed:",
        result.jobs_changed,
    )

    print(
        "Errors:",
        len(result.errors),
    )

    print()
    print(
        "========== DATABASE RUN VERIFICATION =========="
    )

    latest_run = (
        session.query(
            __import__(
                "app.database.ingestion_run_model",
                fromlist=["IngestionRunModel"],
            ).IngestionRunModel
        )
        .order_by(
            __import__(
                "app.database.ingestion_run_model",
                fromlist=["IngestionRunModel"],
            ).IngestionRunModel.id.desc()
        )
        .first()
    )

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
        "Database jobs fetched:",
        latest_run.jobs_fetched,
    )

    print(
        "Database jobs new:",
        latest_run.jobs_new,
    )

    print(
        "Finished:",
        latest_run.finished_at is not None,
    )

finally:

    session.close()