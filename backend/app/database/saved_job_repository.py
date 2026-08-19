from datetime import datetime, timezone
from typing import Optional, Tuple, List
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.database.saved_job_model import SavedJobModel
from app.database.job_model import JobModel


class SavedJobRepository:

    def __init__(self, session: Session):
        self.session = session

    def is_saved(self, user_id: int, job_id: int) -> bool:
        stmt = select(SavedJobModel.id).where(
            SavedJobModel.user_id == user_id,
            SavedJobModel.job_id == job_id,
        )
        return self.session.execute(stmt).scalar_one_or_none() is not None

    def get_by_user_and_job(self, user_id: int, job_id: int) -> Optional[SavedJobModel]:
        stmt = select(SavedJobModel).where(
            SavedJobModel.user_id == user_id,
            SavedJobModel.job_id == job_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def save_job(
        self,
        user_id: int,
        job_id: int,
        notes: Optional[str] = None,
    ) -> SavedJobModel:
        existing = self.get_by_user_and_job(user_id, job_id)
        if existing:
            if notes is not None:
                existing.notes = notes.strip() if notes else None
            self.session.commit()
            self.session.refresh(existing)
            return existing

        now = datetime.now(timezone.utc)
        saved_job = SavedJobModel(
            user_id=user_id,
            job_id=job_id,
            notes=notes.strip() if notes else None,
            created_at=now,
        )
        self.session.add(saved_job)
        self.session.commit()
        self.session.refresh(saved_job)
        return saved_job

    def unsave_job(self, user_id: int, job_id: int) -> bool:
        existing = self.get_by_user_and_job(user_id, job_id)
        if not existing:
            return False
        self.session.delete(existing)
        self.session.commit()
        return True

    def get_saved_jobs(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[SavedJobModel], int]:
        now = datetime.now(timezone.utc)

        # Base query joined with jobs table, excluding deleted/expired jobs
        stmt = (
            select(SavedJobModel)
            .join(JobModel, SavedJobModel.job_id == JobModel.id)
            .where(
                SavedJobModel.user_id == user_id,
                JobModel.is_deleted == False,
                and_(
                    JobModel.expires_at.is_(None) | (JobModel.expires_at >= now)
                ),
            )
            .order_by(SavedJobModel.created_at.desc())
        )

        count_stmt = (
            select(func.count(SavedJobModel.id))
            .join(JobModel, SavedJobModel.job_id == JobModel.id)
            .where(
                SavedJobModel.user_id == user_id,
                JobModel.is_deleted == False,
                and_(
                    JobModel.expires_at.is_(None) | (JobModel.expires_at >= now)
                ),
            )
        )

        total = self.session.execute(count_stmt).scalar_one()

        saved_jobs = list(
            self.session.execute(
                stmt.offset(offset).limit(limit)
            ).scalars().all()
        )

        return saved_jobs, total
