from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base


class IngestionRunModel(Base):

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    pages_attempted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    pages_succeeded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    pages_failed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_fetched: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_valid: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_invalid: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_new: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_duplicate: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_changed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )