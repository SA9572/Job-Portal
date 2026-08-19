from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Query,
)

from app.database.config import SessionLocal
from app.database.job_repository import JobRepository
from app.database.job_change_repository import JobChangeRepository
from app.database.ingestion_run_repository import (
    IngestionRunRepository,
)
from app.database.ingestion_error_repository import (
    IngestionErrorRepository,
)
from app.services.persistent_deduplicator import PersistentJobDeduplicator
from app.services.validator import JobValidator
from app.services.ingestion_service import IngestionService
from app.sources.himalayas import HimalayasSource
from app.models.responses import (
    IngestionErrorListResponse,
    IngestionRunListResponse,
    IngestionRunResponse,
    IngestionTriggerRequest,
    IngestionTriggerResponse,
)


router = APIRouter()


# =========================================
# GET INGESTION RUNS (LIST)
# =========================================

@router.get(
    "/runs",
    response_model=IngestionRunListResponse,
)
def get_ingestion_runs(
    source: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):

    session = SessionLocal()

    try:

        repository = IngestionRunRepository(session)

        runs, total = repository.get_runs_paginated(
            source=source,
            status=status,
            limit=limit,
            offset=offset,
        )

        return {
            "count": len(runs),
            "total": total,
            "limit": limit,
            "offset": offset,
            "runs": runs,
        }

    finally:

        session.close()


# =========================================
# GET SINGLE INGESTION RUN
# =========================================

@router.get(
    "/runs/{run_id}",
    response_model=IngestionRunResponse,
)
def get_ingestion_run_detail(
    run_id: int,
):

    session = SessionLocal()

    try:

        repository = IngestionRunRepository(session)

        run = repository.get_by_id(run_id)

        if run is None:

            raise HTTPException(
                status_code=404,
                detail="Ingestion run not found",
            )

        return run

    finally:

        session.close()


# =========================================
# GET INGESTION ERRORS FOR RUN
# =========================================

@router.get(
    "/runs/{run_id}/errors",
    response_model=IngestionErrorListResponse,
)
def get_ingestion_run_errors(
    run_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):

    session = SessionLocal()

    try:

        run_repo = IngestionRunRepository(session)

        run = run_repo.get_by_id(run_id)

        if run is None:

            raise HTTPException(
                status_code=404,
                detail="Ingestion run not found",
            )

        error_repo = IngestionErrorRepository(session)

        errors, total = error_repo.get_by_run_id_paginated(
            ingestion_run_id=run_id,
            limit=limit,
            offset=offset,
        )

        return {
            "count": len(errors),
            "total": total,
            "limit": limit,
            "offset": offset,
            "errors": errors,
        }

    finally:

        session.close()


# =========================================
# TRIGGER INGESTION RUN
# =========================================

@router.post(
    "/run",
    response_model=IngestionTriggerResponse,
)
def trigger_ingestion_run(
    body: IngestionTriggerRequest = IngestionTriggerRequest(),
):

    # -----------------------------------------
    # VALIDATE PARAMETER BOUNDS
    # -----------------------------------------

    if body.max_pages < 1 or body.max_pages > 20:

        raise HTTPException(
            status_code=400,
            detail="max_pages must be between 1 and 20",
        )

    if body.page_size < 1 or body.page_size > 100:

        raise HTTPException(
            status_code=400,
            detail="page_size must be between 1 and 100",
        )

    session = SessionLocal()

    try:

        ingestion_run_repo = IngestionRunRepository(session)

        # -----------------------------------------
        # CONCURRENCY CHECK
        # -----------------------------------------

        if ingestion_run_repo.has_active_run():

            raise HTTPException(
                status_code=409,
                detail="An ingestion run is currently in progress",
            )

        job_repo = JobRepository(session)
        change_repo = JobChangeRepository(session)
        ingestion_error_repo = IngestionErrorRepository(session)

        validator = JobValidator()
        deduplicator = PersistentJobDeduplicator(
            repository=job_repo,
            change_repository=change_repo,
        )

        source = HimalayasSource()

        service = IngestionService(
            source=source,
            validator=validator,
            deduplicator=deduplicator,
            ingestion_run_repository=ingestion_run_repo,
            ingestion_error_repository=ingestion_error_repo,
        )

        # -----------------------------------------
        # EXECUTE INGESTION
        # -----------------------------------------

        result = service.run(
            max_pages=body.max_pages,
            page_size=body.page_size,
        )

        return {
            "message": "Ingestion completed successfully",
            "source": result.source,
            "pages_attempted": result.pages_attempted,
            "pages_succeeded": result.pages_succeeded,
            "pages_failed": result.pages_failed,
            "jobs_fetched": result.jobs_fetched,
            "jobs_valid": result.jobs_valid,
            "jobs_invalid": result.jobs_invalid,
            "jobs_new": result.jobs_new,
            "jobs_duplicate": result.jobs_duplicate,
            "jobs_changed": result.jobs_changed,
            "errors_count": len(result.errors),
        }

    finally:

        session.close()


# =========================================
# BACKGROUND INGESTION WORKER
# =========================================

def _run_ingestion_in_background(
    max_pages: int,
    page_size: int,
):

    session = SessionLocal()

    try:

        ingestion_run_repo = IngestionRunRepository(session)
        job_repo = JobRepository(session)
        change_repo = JobChangeRepository(session)
        ingestion_error_repo = IngestionErrorRepository(session)

        validator = JobValidator()
        deduplicator = PersistentJobDeduplicator(
            repository=job_repo,
            change_repository=change_repo,
        )

        source = HimalayasSource()

        service = IngestionService(
            source=source,
            validator=validator,
            deduplicator=deduplicator,
            ingestion_run_repository=ingestion_run_repo,
            ingestion_error_repository=ingestion_error_repo,
        )

        service.run(
            max_pages=max_pages,
            page_size=page_size,
        )

    finally:

        session.close()


# =========================================
# TRIGGER ASYNC BACKGROUND INGESTION RUN
# =========================================

@router.post(
    "/run-async",
    status_code=202,
)
def trigger_ingestion_run_async(
    background_tasks: BackgroundTasks,
    body: IngestionTriggerRequest = IngestionTriggerRequest(),
):

    if body.max_pages < 1 or body.max_pages > 20:

        raise HTTPException(
            status_code=400,
            detail="max_pages must be between 1 and 20",
        )

    if body.page_size < 1 or body.page_size > 100:

        raise HTTPException(
            status_code=400,
            detail="page_size must be between 1 and 100",
        )

    session = SessionLocal()

    try:

        ingestion_run_repo = IngestionRunRepository(session)

        if ingestion_run_repo.has_active_run():

            raise HTTPException(
                status_code=409,
                detail="An ingestion run is currently in progress",
            )

    finally:

        session.close()

    background_tasks.add_task(
        _run_ingestion_in_background,
        max_pages=body.max_pages,
        page_size=body.page_size,
    )

    return {
        "message": "Ingestion job started in background",
        "status": "accepted",
    }
