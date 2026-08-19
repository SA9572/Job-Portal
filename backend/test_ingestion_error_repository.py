from datetime import datetime, timezone

from app.database.config import SessionLocal
from app.database.ingestion_error_repository import (
    IngestionErrorRepository,
)
from app.database.ingestion_run_repository import (
    IngestionRunRepository,
)
from app.models.ingestion import IngestionError


session = SessionLocal()

try:

    run_repository = IngestionRunRepository(
        session
    )

    error_repository = (
        IngestionErrorRepository(
            session
        )
    )

    print(
        "========== INGESTION ERROR REPOSITORY TEST =========="
    )

    # -----------------------------------------
    # CREATE INGESTION RUN
    # -----------------------------------------

    run = run_repository.create(
        source="test"
    )

    print(
        "Created ingestion run ID:",
        run.id,
    )

    # -----------------------------------------
    # CREATE ERROR
    # -----------------------------------------

    error = IngestionError(
        source="test",

        page_number=2,

        offset=20,

        status_code=503,

        attempts=3,

        error_type="HttpRequestError",

        message=(
            "Retryable HTTP status: 503"
        ),

        occurred_at=datetime.now(
            timezone.utc
        ),
    )

    saved_error = (
        error_repository.create(
            ingestion_run_id=run.id,
            error=error,
        )
    )

    print()
    print(
        "========== CREATE TEST =========="
    )

    print(
        "Error ID:",
        saved_error.id,
    )

    print(
        "Run ID:",
        saved_error.ingestion_run_id,
    )

    print(
        "Source:",
        saved_error.source,
    )

    print(
        "Page:",
        saved_error.page_number,
    )

    print(
        "Offset:",
        saved_error.offset,
    )

    print(
        "Status:",
        saved_error.status_code,
    )

    print(
        "Attempts:",
        saved_error.attempts,
    )

    print(
        "Error Type:",
        saved_error.error_type,
    )

    print(
        "Message:",
        saved_error.message,
    )

    # -----------------------------------------
    # READ ERRORS
    # -----------------------------------------

    errors = (
        error_repository.get_by_run_id(
            run.id
        )
    )

    print()
    print(
        "========== READ TEST =========="
    )

    print(
        "Errors found:",
        len(errors),
    )

    if errors:

        first_error = errors[0]

        print(
            "First error page:",
            first_error.page_number,
        )

        print(
            "First error status:",
            first_error.status_code,
        )

finally:

    session.close()