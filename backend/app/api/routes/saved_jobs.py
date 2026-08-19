from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.database.user_model import UserModel
from app.database.job_repository import JobRepository
from app.database.saved_job_repository import SavedJobRepository
from app.models.saved_job import (
    SaveJobRequest,
    SavedJobResponse,
    SavedJobListResponse,
    SaveStatusResponse,
)

router = APIRouter()


@router.post(
    "/{job_id}",
    response_model=SavedJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_job(
    job_id: int,
    req: Optional[SaveJobRequest] = None,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    job_repo = JobRepository(session)
    job = job_repo.get_by_id(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    saved_repo = SavedJobRepository(session)
    notes = req.notes if req else None
    saved_item = saved_repo.save_job(
        user_id=current_user.id,
        job_id=job_id,
        notes=notes,
    )

    return saved_item


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
)
def unsave_job(
    job_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    saved_repo = SavedJobRepository(session)
    removed = saved_repo.unsave_job(user_id=current_user.id, job_id=job_id)

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found",
        )

    return {"message": "Job unsaved successfully", "job_id": job_id}


@router.get(
    "",
    response_model=SavedJobListResponse,
)
def get_saved_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    saved_repo = SavedJobRepository(session)
    items, total = saved_repo.get_saved_jobs(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    return {
        "count": len(items),
        "total": total,
        "limit": limit,
        "offset": offset,
        "jobs": items,
    }


@router.get(
    "/{job_id}/check",
    response_model=SaveStatusResponse,
)
def check_saved_status(
    job_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    saved_repo = SavedJobRepository(session)
    is_saved = saved_repo.is_saved(user_id=current_user.id, job_id=job_id)
    return {
        "job_id": job_id,
        "is_saved": is_saved,
    }
