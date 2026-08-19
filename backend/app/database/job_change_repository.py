from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.job_change_model import JobChangeModel


class JobChangeRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        job_id: int,
        source: str,
        external_id: str,
        old_content_hash: str,
        new_content_hash: str,
    ) -> JobChangeModel:

        change = JobChangeModel(
            job_id=job_id,

            source=source,

            external_id=external_id,

            old_content_hash=old_content_hash,

            new_content_hash=new_content_hash,

            changed_at=datetime.now(
                timezone.utc
            ),

            created_at=datetime.now(
                timezone.utc
            ),
        )

        self.session.add(change)

        self.session.commit()

        self.session.refresh(change)

        return change

    def get_by_job_id(
        self,
        job_id: int,
    ) -> list[JobChangeModel]:

        return list(
            self.session.query(
                JobChangeModel
            )
            .filter(
                JobChangeModel.job_id
                == job_id
            )
            .order_by(
                JobChangeModel.id
            )
            .all()
        )

    def get_by_external_id(
        self,
        source: str,
        external_id: str,
    ) -> list[JobChangeModel]:

        return list(
            self.session.query(
                JobChangeModel
            )
            .filter(
                JobChangeModel.source
                == source
            )
            .filter(
                JobChangeModel.external_id
                == external_id
            )
            .order_by(
                JobChangeModel.id
            )
            .all()
        )

    def get_by_id(
        self,
        change_id: int,
    ) -> JobChangeModel | None:

        return self.session.get(
            JobChangeModel,
            change_id,
        )

    def get_by_job_id_paginated(
        self,
        job_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[JobChangeModel], int]:

        query = (
            self.session.query(JobChangeModel)
            .filter(JobChangeModel.job_id == job_id)
        )

        total = query.count()

        changes = list(
            query.order_by(JobChangeModel.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return changes, total