from app.database.job_change_repository import (
    JobChangeRepository,
)
from app.database.job_repository import JobRepository
from app.models.job import Job


class PersistentJobDeduplicator:

    def __init__(
        self,
        repository: JobRepository,
        change_repository: JobChangeRepository | None = None,
    ):
        self.repository = repository
        self.change_repository = change_repository

    def check(
        self,
        job: Job,
    ) -> str:

        existing = self.repository.get_by_identity(
            source=job.source,
            external_id=job.external_id,
        )

        # ---------------------------------
        # NEW JOB
        # ---------------------------------

        if existing is None:

            self.repository.create(job)

            return "new"

        # ---------------------------------
        # DUPLICATE
        # ---------------------------------

        if (
            existing.content_hash
            == job.content_hash
        ):

            return "duplicate"

        # ---------------------------------
        # CHANGED JOB
        # ---------------------------------

        old_content_hash = (
            existing.content_hash
        )

        new_content_hash = (
            job.content_hash
        )

        # ---------------------------------
        # SAVE CHANGE HISTORY
        # ---------------------------------

        if self.change_repository is not None:

            self.change_repository.create(

                job_id=existing.id,

                source=job.source,

                external_id=job.external_id,

                old_content_hash=(
                    old_content_hash
                ),

                new_content_hash=(
                    new_content_hash
                ),
            )

        # ---------------------------------
        # UPDATE CURRENT JOB
        # ---------------------------------

        self.repository.update(
            existing,
            job,
        )

        return "changed"