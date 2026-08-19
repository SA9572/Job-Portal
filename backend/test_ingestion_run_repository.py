from app.database.config import SessionLocal
from app.database.ingestion_run_repository import (
    IngestionRunRepository,
)


session = SessionLocal()

try:

    repository = IngestionRunRepository(
        session
    )

    print(
        "========== INGESTION RUN REPOSITORY TEST =========="
    )

    # ---------------------------------
    # CREATE
    # ---------------------------------

    run = repository.create(
        source="test"
    )

    print(
        "Created run ID:",
        run.id,
    )

    print(
        "Initial status:",
        run.status,
    )

    print(
        "Initial finished_at:",
        run.finished_at,
    )

    # ---------------------------------
    # UPDATE
    # ---------------------------------

    updated = repository.update_result(
        run,

        pages_attempted=5,
        pages_succeeded=4,
        pages_failed=1,

        jobs_fetched=80,
        jobs_valid=78,
        jobs_invalid=2,

        jobs_new=60,
        jobs_duplicate=15,
        jobs_changed=3,

        status="partial_failure",
    )

    print()
    print(
        "========== UPDATED RESULT =========="
    )

    print(
        "Pages attempted:",
        updated.pages_attempted,
    )

    print(
        "Pages succeeded:",
        updated.pages_succeeded,
    )

    print(
        "Pages failed:",
        updated.pages_failed,
    )

    print(
        "Jobs fetched:",
        updated.jobs_fetched,
    )

    print(
        "Jobs valid:",
        updated.jobs_valid,
    )

    print(
        "Jobs invalid:",
        updated.jobs_invalid,
    )

    print(
        "Jobs new:",
        updated.jobs_new,
    )

    print(
        "Jobs duplicate:",
        updated.jobs_duplicate,
    )

    print(
        "Jobs changed:",
        updated.jobs_changed,
    )

    print(
        "Status:",
        updated.status,
    )

    print(
        "Finished:",
        updated.finished_at is not None,
    )

    # ---------------------------------
    # READ
    # ---------------------------------

    saved = repository.get_by_id(
        run.id
    )

    print()
    print(
        "========== READ TEST =========="
    )

    print(
        "Run found:",
        saved is not None,
    )

    print(
        "Saved status:",
        saved.status if saved else None,
    )

finally:

    session.close()