from app.database.config import SessionLocal

from app.database.job_repository import JobRepository
from app.database.job_change_repository import (
    JobChangeRepository,
)

from app.database.ingestion_run_repository import (
    IngestionRunRepository,
)

from app.database.ingestion_error_repository import (
    IngestionErrorRepository,
)

from app.services.persistent_deduplicator import (
    PersistentJobDeduplicator,
)

from app.services.validator import JobValidator

from app.services.ingestion_service import (
    IngestionService,
)

from app.sources.himalayas import (
    HimalayasSource,
)


def main():

    print()
    print("========================================")
    print("       JOB INGESTION PIPELINE")
    print("========================================")

    session = SessionLocal()

    try:

        # =====================================
        # CREATE REPOSITORIES
        # =====================================

        job_repository = JobRepository(
            session
        )

        change_repository = (
            JobChangeRepository(
                session
            )
        )

        ingestion_run_repository = (
            IngestionRunRepository(
                session
            )
        )

        ingestion_error_repository = (
            IngestionErrorRepository(
                session
            )
        )

        # =====================================
        # CREATE SOURCE
        # =====================================

        source = HimalayasSource()

        # =====================================
        # CREATE VALIDATOR
        # =====================================

        validator = JobValidator()

        # =====================================
        # CREATE PERSISTENT DEDUPLICATOR
        # =====================================

        deduplicator = (
            PersistentJobDeduplicator(

                repository=job_repository,

                change_repository=(
                    change_repository
                ),
            )
        )

        # =====================================
        # CREATE INGESTION SERVICE
        # =====================================

        service = IngestionService(

            source=source,

            validator=validator,

            deduplicator=deduplicator,

            ingestion_run_repository=(
                ingestion_run_repository
            ),

            ingestion_error_repository=(
                ingestion_error_repository
            ),
        )

        # =====================================
        # RUN INGESTION
        # =====================================

        result = service.run(

            max_pages=5,

            page_size=20,
        )

        # =====================================
        # DISPLAY RESULT
        # =====================================

        print()
        print("========================================")
        print("         INGESTION COMPLETED")
        print("========================================")

        print(
            "Source:",
            result.source,
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

        # =====================================
        # DISPLAY ERRORS
        # =====================================

        if result.errors:

            print()
            print(
                "========================================"
            )

            print(
                "             INGESTION ERRORS"
            )

            print(
                "========================================"
            )

            for error in result.errors:

                print()
                print(
                    "Page:",
                    error.page_number,
                )

                print(
                    "Offset:",
                    error.offset,
                )

                print(
                    "Status:",
                    error.status_code,
                )

                print(
                    "Attempts:",
                    error.attempts,
                )

                print(
                    "Type:",
                    error.error_type,
                )

                print(
                    "Message:",
                    error.message,
                )

        print()
        print("========================================")
        print("              PIPELINE DONE")
        print("========================================")

    finally:

        session.close()


if __name__ == "__main__":
    main()