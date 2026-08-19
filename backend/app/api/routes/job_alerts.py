from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.database.user_model import UserModel
from app.database.job_alert_repository import JobAlertRepository
from app.models.job_alert import (
    JobAlertCreateRequest,
    JobAlertUpdateRequest,
    JobAlertResponse,
    JobAlertListResponse,
    AlertMatchResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=JobAlertResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_alert(
    req: JobAlertCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    repo = JobAlertRepository(session)
    alert = repo.create(
        user_id=current_user.id,
        name=req.name,
        keywords=req.keywords,
        location=req.location,
        category=req.category,
        seniority=req.seniority,
        min_salary=req.min_salary,
        frequency=req.frequency,
        is_active=req.is_active,
    )
    return alert


@router.get(
    "",
    response_model=JobAlertListResponse,
)
def get_alerts(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    repo = JobAlertRepository(session)
    alerts, total = repo.get_user_alerts(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return {
        "count": len(alerts),
        "total": total,
        "limit": limit,
        "offset": offset,
        "alerts": alerts,
    }


@router.get(
    "/{alert_id}",
    response_model=JobAlertResponse,
)
def get_alert_detail(
    alert_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    repo = JobAlertRepository(session)
    alert = repo.get_by_id(alert_id, current_user.id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job alert not found",
        )
    return alert


@router.put(
    "/{alert_id}",
    response_model=JobAlertResponse,
)
def update_alert(
    alert_id: int,
    req: JobAlertUpdateRequest,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    repo = JobAlertRepository(session)
    alert = repo.get_by_id(alert_id, current_user.id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job alert not found",
        )

    updated_alert = repo.update(
        alert=alert,
        name=req.name,
        keywords=req.keywords,
        location=req.location,
        category=req.category,
        seniority=req.seniority,
        min_salary=req.min_salary,
        frequency=req.frequency,
        is_active=req.is_active,
    )
    return updated_alert


@router.delete(
    "/{alert_id}",
    status_code=status.HTTP_200_OK,
)
def delete_alert(
    alert_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    repo = JobAlertRepository(session)
    deleted = repo.delete(alert_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job alert not found",
        )
    return {"message": "Job alert deleted successfully", "alert_id": alert_id}


@router.post(
    "/{alert_id}/test-match",
    response_model=AlertMatchResponse,
)
def test_alert_match(
    alert_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    repo = JobAlertRepository(session)
    alert = repo.get_by_id(alert_id, current_user.id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job alert not found",
        )

    jobs, total = repo.find_matching_jobs(alert=alert, limit=limit, offset=offset)

    return {
        "alert_id": alert.id,
        "alert_name": alert.name,
        "count": len(jobs),
        "total": total,
        "jobs": jobs,
    }
