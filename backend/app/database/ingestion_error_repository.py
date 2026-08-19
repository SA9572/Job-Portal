from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.ingestion_error_model import (
    IngestionErrorModel,
)
from app.models.ingestion import IngestionError


class IngestionErrorRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        ingestion_run_id: int,
        error: IngestionError,
    ) -> IngestionErrorModel:

        error_model = IngestionErrorModel(
            ingestion_run_id=ingestion_run_id,

            source=error.source,

            page_number=error.page_number,

            offset=error.offset,

            status_code=error.status_code,

            attempts=error.attempts,

            error_type=error.error_type,

            message=error.message,

            occurred_at=error.occurred_at,

            created_at=datetime.now(
                timezone.utc
            ),
        )

        self.session.add(error_model)

        self.session.commit()

        self.session.refresh(error_model)

        return error_model

    def get_by_run_id(
        self,
        ingestion_run_id: int,
    ) -> list[IngestionErrorModel]:

        return list(
            self.session.query(
                IngestionErrorModel
            )
            .filter(
                IngestionErrorModel.ingestion_run_id
                == ingestion_run_id
            )
            .order_by(
                IngestionErrorModel.id
            )
            .all()
        )

    def get_by_run_id_paginated(
        self,
        ingestion_run_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[IngestionErrorModel], int]:

        query = (
            self.session.query(IngestionErrorModel)
            .filter(IngestionErrorModel.ingestion_run_id == ingestion_run_id)
        )

        total = query.count()

        errors = list(
            query.order_by(IngestionErrorModel.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return errors, total