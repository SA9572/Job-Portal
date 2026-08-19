from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_optional_current_user
from app.database.user_model import UserModel
from app.database.job_repository import JobRepository
from app.services.matching_engine import JobMatchingEngine
from app.models.job_match import (
    UserProfileMatchRequest,
    MatchedJobListResponse,
    SingleJobMatchResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=MatchedJobListResponse,
)
def match_jobs(
    req: UserProfileMatchRequest,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    min_score: float = Query(default=0.1, ge=0.0, le=1.0),
    current_user: UserModel | None = Depends(get_optional_current_user),
    session: Session = Depends(get_db),
):
    profile = req.model_dump()
    jobs, total = JobMatchingEngine.match_jobs_for_user(
        session=session,
        profile=profile,
        limit=limit,
        offset=offset,
        min_score=min_score,
    )

    return {
        "count": len(jobs),
        "total": total,
        "limit": limit,
        "offset": offset,
        "jobs": jobs,
    }


@router.post(
    "/{job_id}",
    response_model=SingleJobMatchResponse,
)
def match_single_job(
    job_id: int,
    req: UserProfileMatchRequest,
    current_user: UserModel | None = Depends(get_optional_current_user),
    session: Session = Depends(get_db),
):
    job_repo = JobRepository(session)
    job = job_repo.get_by_id(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    profile = req.model_dump()
    score, breakdown = JobMatchingEngine.calculate_user_match(profile, job)

    return {
        "job_id": job.id,
        "job_title": job.title,
        "match_score": score,
        "match_breakdown": breakdown,
    }
