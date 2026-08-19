from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.ingestion_run_model import (
    IngestionRunModel,
)


class IngestionRunRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        source: str,
    ) -> IngestionRunModel:

        run = IngestionRunModel(
            source=source,

            started_at=datetime.now(
                timezone.utc
            ),

            finished_at=None,

            pages_attempted=0,
            pages_succeeded=0,
            pages_failed=0,

            jobs_fetched=0,
            jobs_valid=0,
            jobs_invalid=0,

            jobs_new=0,
            jobs_duplicate=0,
            jobs_changed=0,

            status="running",

            created_at=datetime.now(
                timezone.utc
            ),
        )

        self.session.add(run)

        self.session.commit()

        self.session.refresh(run)

        return run

    def update_result(
        self,
        run: IngestionRunModel,
        *,
        pages_attempted: int,
        pages_succeeded: int,
        pages_failed: int,
        jobs_fetched: int,
        jobs_valid: int,
        jobs_invalid: int,
        jobs_new: int,
        jobs_duplicate: int,
        jobs_changed: int,
        status: str,
    ) -> IngestionRunModel:

        run.pages_attempted = pages_attempted
        run.pages_succeeded = pages_succeeded
        run.pages_failed = pages_failed

        run.jobs_fetched = jobs_fetched
        run.jobs_valid = jobs_valid
        run.jobs_invalid = jobs_invalid

        run.jobs_new = jobs_new
        run.jobs_duplicate = jobs_duplicate
        run.jobs_changed = jobs_changed

        run.status = status

        run.finished_at = datetime.now(
            timezone.utc
        )

        self.session.commit()

        self.session.refresh(run)

        return run

    def get_by_id(
        self,
        run_id: int,
    ) -> IngestionRunModel | None:

        return self.session.get(
            IngestionRunModel,
            run_id,
        )

    def get_runs_paginated(
        self,
        source: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[IngestionRunModel], int]:

        query = self.session.query(IngestionRunModel)

        if source:
            query = query.filter(IngestionRunModel.source == source)

        if status:
            query = query.filter(IngestionRunModel.status == status)

        total = query.count()

        runs = list(
            query.order_by(IngestionRunModel.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return runs, total

    def has_active_run(self) -> bool:

        active_count = (
            self.session.query(IngestionRunModel)
            .filter(IngestionRunModel.status == "running")
            .count()
        )

        return active_count > 0