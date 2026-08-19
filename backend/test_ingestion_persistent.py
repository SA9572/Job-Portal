from app.database.config import SessionLocal
from app.database.job_repository import JobRepository
from app.services.ingestion_service import IngestionService
from app.services.persistent_deduplicator import (
    PersistentJobDeduplicator,
)
from app.services.validator import JobValidator
from app.sources.himalayas import HimalayasSource


session = SessionLocal()

try:

    repository = JobRepository(session)

    deduplicator = PersistentJobDeduplicator(
        repository
    )

    service = IngestionService(
        source=HimalayasSource(),
        validator=JobValidator(),
        deduplicator=deduplicator,
    )

    print(
        "========== PERSISTENT INGESTION TEST =========="
    )

    result = service.run(
        max_pages=1,
        page_size=20,
    )

    print()
    print(
        "========== FIRST INGESTION =========="
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

finally:

    session.close()