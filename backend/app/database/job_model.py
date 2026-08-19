from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class JobModel(Base):

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    external_id: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    excerpt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    company: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    company_slug: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    company_logo: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    employment_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    minimum_salary: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    maximum_salary: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    salary_period: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    currency: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    seniority: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    location_restrictions: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    timezone_restrictions: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    categories: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    parent_categories: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    application_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    source_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # =========================================
    # SOFT DELETE
    # =========================================

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    __table_args__ = (
        UniqueConstraint(
            "source",
            "external_id",
            name="uq_jobs_source_external_id",
        ),
        Index("ix_jobs_published_at", "published_at"),
        Index("ix_jobs_company", "company"),
        Index("ix_jobs_employment_type", "employment_type"),
        Index("ix_jobs_minimum_salary", "minimum_salary"),
        Index("ix_jobs_maximum_salary", "maximum_salary"),
        Index("ix_jobs_created_at", "created_at"),
        Index("ix_jobs_source", "source"),
        Index("ix_jobs_is_deleted", "is_deleted"),
        Index("ix_jobs_expires_at", "expires_at"),
    )