from datetime import datetime, timezone
from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database.job_alert_model import JobAlertModel
from app.database.job_repository import JobRepository
from app.database.job_model import JobModel


class JobAlertRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, alert_id: int, user_id: int) -> Optional[JobAlertModel]:
        stmt = select(JobAlertModel).where(
            JobAlertModel.id == alert_id,
            JobAlertModel.user_id == user_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def create(
        self,
        user_id: int,
        name: str,
        keywords: Optional[str] = None,
        location: Optional[str] = None,
        category: Optional[str] = None,
        seniority: Optional[str] = None,
        min_salary: Optional[float] = None,
        frequency: str = "daily",
        is_active: bool = True,
    ) -> JobAlertModel:
        now = datetime.now(timezone.utc)
        alert = JobAlertModel(
            user_id=user_id,
            name=name.strip(),
            keywords=keywords.strip() if keywords else None,
            location=location.strip() if location else None,
            category=category.strip() if category else None,
            seniority=seniority.strip() if seniority else None,
            min_salary=min_salary if (min_salary is not None and min_salary >= 0) else None,
            frequency=frequency.strip().lower() if frequency else "daily",
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

        self.session.add(alert)
        self.session.commit()
        self.session.refresh(alert)
        return alert

    def update(
        self,
        alert: JobAlertModel,
        name: Optional[str] = None,
        keywords: Optional[str] = None,
        location: Optional[str] = None,
        category: Optional[str] = None,
        seniority: Optional[str] = None,
        min_salary: Optional[float] = None,
        frequency: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> JobAlertModel:
        if name is not None:
            alert.name = name.strip()
        if keywords is not None:
            alert.keywords = keywords.strip() if keywords else None
        if location is not None:
            alert.location = location.strip() if location else None
        if category is not None:
            alert.category = category.strip() if category else None
        if seniority is not None:
            alert.seniority = seniority.strip() if seniority else None
        if min_salary is not None:
            alert.min_salary = min_salary if min_salary >= 0 else None
        if frequency is not None:
            alert.frequency = frequency.strip().lower() if frequency else "daily"
        if is_active is not None:
            alert.is_active = is_active

        alert.updated_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(alert)
        return alert

    def delete(self, alert_id: int, user_id: int) -> bool:
        alert = self.get_by_id(alert_id, user_id)
        if not alert:
            return False
        self.session.delete(alert)
        self.session.commit()
        return True

    def get_user_alerts(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[JobAlertModel], int]:
        stmt = (
            select(JobAlertModel)
            .where(JobAlertModel.user_id == user_id)
            .order_by(JobAlertModel.id.desc())
        )

        count_stmt = select(func.count(JobAlertModel.id)).where(JobAlertModel.user_id == user_id)
        total = self.session.execute(count_stmt).scalar_one()

        alerts = list(
            self.session.execute(stmt.offset(offset).limit(limit)).scalars().all()
        )

        return alerts, total

    def find_matching_jobs(
        self,
        alert: JobAlertModel,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[List[JobModel], int]:
        """Runs candidate search against JobRepository based on alert criteria."""
        job_repo = JobRepository(self.session)
        location_param = [alert.location] if alert.location else None
        category_param = [alert.category] if alert.category else None
        seniority_param = [alert.seniority] if alert.seniority else None

        return job_repo.get_jobs(
            limit=limit,
            offset=offset,
            search=alert.keywords,
            location=location_param,
            category=category_param,
            seniority=seniority_param,
            minimum_salary=alert.min_salary,
            include_expired=False,
            include_deleted=False,
        )
