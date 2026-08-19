from datetime import datetime, timezone

from app.models.ingestion import (
    IngestionError,
    IngestionResult,
)
from app.services.deduplicator import JobDeduplicator
from app.services.http_client import HttpRequestError
from app.services.sanitizer import DataSanitizer
from app.services.validator import JobValidator
from app.sources.base import JobSource
from app.sources.himalayas import HimalayasSource


class IngestionService:

    def __init__(
        self,
        source: JobSource | None = None,
        validator: JobValidator | None = None,
        deduplicator=None,
        ingestion_run_repository=None,
        ingestion_error_repository=None,
    ):

        self.source: JobSource = (
            source
            or HimalayasSource()
        )

        self.validator = (
            validator
            or JobValidator()
        )

        if deduplicator is not None:

            self.deduplicator = (
                deduplicator
            )

        else:

            self.deduplicator = (
                JobDeduplicator()
            )

        self.ingestion_run_repository = (
            ingestion_run_repository
        )

        self.ingestion_error_repository = (
            ingestion_error_repository
        )

    def run(
        self,
        max_pages: int = 5,
        page_size: int = 20,
    ) -> IngestionResult:

        source_name = getattr(self.source, "source_name", "himalayas")

        pages_attempted = 0
        pages_succeeded = 0
        pages_failed = 0

        jobs_fetched = 0
        jobs_valid = 0
        jobs_invalid = 0

        jobs_new = 0
        jobs_duplicate = 0
        jobs_changed = 0

        errors: list[IngestionError] = []

        # =========================================
        # START INGESTION RUN
        # =========================================

        ingestion_run = None

        if self.ingestion_run_repository:

            ingestion_run = (
                self.ingestion_run_repository.create(
                    source=source_name
                )
            )

        # =========================================
        # PROCESS PAGES
        # =========================================

        for page_number in range(max_pages):

            pages_attempted += 1

            offset = (
                page_number * page_size
            )

            try:

                jobs = self.source.fetch_jobs(
                    limit=page_size,
                    offset=offset,
                )

                if not jobs:
                    break

                pages_succeeded += 1

                jobs_fetched += len(jobs)

                # =================================
                # PROCESS JOBS
                # =================================

                for job in jobs:

                    job = DataSanitizer.sanitize(job)

                    validation_errors = (
                        self.validator.validate(
                            job
                        )
                    )

                    if validation_errors:

                        jobs_invalid += 1

                        continue

                    jobs_valid += 1

                    result = (
                        self.deduplicator.check(
                            job
                        )
                    )

                    if result == "new":

                        jobs_new += 1

                    elif result == "duplicate":

                        jobs_duplicate += 1

                    elif result == "changed":

                        jobs_changed += 1

                if len(jobs) < page_size:

                    break

            # =====================================
            # HTTP REQUEST FAILURE
            # =====================================

            except HttpRequestError as exc:

                pages_failed += 1

                error = IngestionError(
                    source=source_name,

                    page_number=(
                        page_number + 1
                    ),

                    offset=offset,

                    status_code=(
                        exc.status_code
                    ),

                    attempts=(
                        exc.attempts
                    ),

                    error_type=(
                        type(exc).__name__
                    ),

                    message=str(exc),

                    occurred_at=(
                        datetime.now(
                            timezone.utc
                        )
                    ),
                )

                errors.append(error)

                # ---------------------------------
                # PERSIST ERROR
                # ---------------------------------

                if (
                    ingestion_run is not None
                    and self.ingestion_error_repository
                ):

                    self.ingestion_error_repository.create(
                        ingestion_run_id=(
                            ingestion_run.id
                        ),
                        error=error,
                    )

                continue

            # =====================================
            # UNEXPECTED FAILURE
            # =====================================

            except Exception as exc:

                pages_failed += 1

                error = IngestionError(
                    source=source_name,

                    page_number=(
                        page_number + 1
                    ),

                    offset=offset,

                    status_code=None,

                    attempts=1,

                    error_type=(
                        type(exc).__name__
                    ),

                    message=str(exc),

                    occurred_at=(
                        datetime.now(
                            timezone.utc
                        )
                    ),
                )

                errors.append(error)

                # ---------------------------------
                # PERSIST ERROR
                # ---------------------------------

                if (
                    ingestion_run is not None
                    and self.ingestion_error_repository
                ):

                    self.ingestion_error_repository.create(
                        ingestion_run_id=(
                            ingestion_run.id
                        ),
                        error=error,
                    )

                continue

        # =========================================
        # DETERMINE FINAL STATUS
        # =========================================

        if pages_failed == 0:

            status = "success"

        elif pages_succeeded > 0:

            status = "partial_failure"

        else:

            status = "failed"

        # =========================================
        # BUILD INGESTION RESULT
        # =========================================

        result = IngestionResult(
            source=source_name,

            pages_attempted=(
                pages_attempted
            ),

            pages_succeeded=(
                pages_succeeded
            ),

            pages_failed=(
                pages_failed
            ),

            jobs_fetched=(
                jobs_fetched
            ),

            jobs_valid=(
                jobs_valid
            ),

            jobs_invalid=(
                jobs_invalid
            ),

            jobs_new=(
                jobs_new
            ),

            jobs_duplicate=(
                jobs_duplicate
            ),

            jobs_changed=(
                jobs_changed
            ),

            errors=errors,
        )

        # =========================================
        # UPDATE INGESTION RUN
        # =========================================

        if (
            ingestion_run is not None
            and self.ingestion_run_repository
        ):

            self.ingestion_run_repository.update_result(

                ingestion_run,

                pages_attempted=(
                    result.pages_attempted
                ),

                pages_succeeded=(
                    result.pages_succeeded
                ),

                pages_failed=(
                    result.pages_failed
                ),

                jobs_fetched=(
                    result.jobs_fetched
                ),

                jobs_valid=(
                    result.jobs_valid
                ),

                jobs_invalid=(
                    result.jobs_invalid
                ),

                jobs_new=(
                    result.jobs_new
                ),

                jobs_duplicate=(
                    result.jobs_duplicate
                ),

                jobs_changed=(
                    result.jobs_changed
                ),

                status=status,
            )

        return result