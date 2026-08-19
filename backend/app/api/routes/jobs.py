from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.database.config import SessionLocal
from app.database.job_repository import JobRepository
from app.database.job_change_repository import JobChangeRepository
from app.services.recommendation_engine import RecommendationEngine
from app.models.responses import (
    FilterOptionsResponse,
    JobChangeListResponse,
    JobChangeResponse,
    JobListResponse,
    JobResponse,
    JobStatsResponse,
    SimilarJobListResponse,
)


router = APIRouter()


# =========================================
# TEST ROUTE
# =========================================

@router.get("/test")
def test_jobs_route():

    return {
        "message": "Jobs API is working"
    }


# =========================================
# GET JOBS
#
# SEARCH
# FILTER
# MULTIPLE-VALUE FILTER
# PAGINATION
# SORTING
# =========================================

@router.get(
    "",
    response_model=JobListResponse,
)
def get_jobs(

    # =====================================
    # PAGINATION
    # =====================================

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

    # =====================================
    # SEARCH
    # =====================================

    search: str | None = Query(
        default=None,
        min_length=1,
    ),

    # =====================================
    # MULTIPLE-VALUE FILTERS
    # =====================================

    company: list[str] | None = Query(
        default=None,
    ),

    employment_type: list[str] | None = Query(
        default=None,
    ),

    location: list[str] | None = Query(
        default=None,
    ),

    seniority: list[str] | None = Query(
        default=None,
    ),

    category: list[str] | None = Query(
        default=None,
    ),

    # =====================================
    # SALARY
    # =====================================

    minimum_salary: float | None = Query(
        default=None,
        ge=0,
    ),

    # =====================================
    # SORTING
    # =====================================

    sort_by: str | None = Query(
        default=None,
    ),

    sort_order: str | None = Query(
        default=None,
    ),

    # =====================================
    # VISIBILITY FLAGS
    # =====================================

    include_expired: bool = Query(
        default=False,
    ),

    include_deleted: bool = Query(
        default=False,
    ),
):

    session = SessionLocal()

    try:

        repository = JobRepository(
            session
        )

        # =================================
        # GET JOBS
        # =================================

        try:

            jobs, total = repository.get_jobs(

                limit=limit,

                offset=offset,

                search=search,

                company=company,

                employment_type=employment_type,

                location=location,

                seniority=seniority,

                category=category,

                minimum_salary=minimum_salary,

                sort_by=sort_by,

                sort_order=sort_order,

                include_expired=include_expired,

                include_deleted=include_deleted,
            )

        except ValueError as exc:

            raise HTTPException(
                status_code=400,
                detail=str(exc),
            )

        # =================================
        # RESPONSE
        # =================================

        return {

            "count": len(jobs),

            "total": total,

            "limit": limit,

            "offset": offset,

            "jobs": [

                {

                    "id": job.id,

                    "source": job.source,

                    "external_id": (
                        job.external_id
                    ),

                    "title": job.title,

                    "excerpt": job.excerpt,

                    "company": job.company,

                    "company_slug": (
                        job.company_slug
                    ),

                    "company_logo": (
                        job.company_logo
                    ),

                    "employment_type": (
                        job.employment_type
                    ),

                    "minimum_salary": (
                        job.minimum_salary
                    ),

                    "maximum_salary": (
                        job.maximum_salary
                    ),

                    "salary_period": (
                        job.salary_period
                    ),

                    "currency": job.currency,

                    "seniority": (
                        job.seniority
                    ),

                    "location_restrictions": (
                        job.location_restrictions
                    ),

                    "timezone_restrictions": (
                        job.timezone_restrictions
                    ),

                    "categories": (
                        job.categories
                    ),

                    "parent_categories": (
                        job.parent_categories
                    ),

                    "description": (
                        job.description
                    ),

                    "published_at": (
                        job.published_at
                    ),

                    "expires_at": (
                        job.expires_at
                    ),

                    "application_url": (
                        job.application_url
                    ),

                    "source_url": (
                        job.source_url
                    ),

                    "content_hash": (
                        job.content_hash
                    ),

                    "fetched_at": (
                        job.fetched_at
                    ),

                    "created_at": (
                        job.created_at
                    ),

                    "updated_at": (
                        job.updated_at
                    ),

                    "is_deleted": (
                        job.is_deleted
                    ),

                    "deleted_at": (
                        job.deleted_at
                    ),
                }

                for job in jobs

            ],
        }

    finally:

        session.close()


# =========================================
# FTS5 FULL-TEXT SEARCH & RELEVANCE
# =========================================

@router.get(
    "/fts/search",
    response_model=JobListResponse,
)
def fts_search_jobs(
    q: str = Query(..., min_length=1, description="FTS search query term/phrase"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    company: list[str] | None = Query(default=None),
    employment_type: list[str] | None = Query(default=None),
    location: list[str] | None = Query(default=None),
    seniority: list[str] | None = Query(default=None),
    category: list[str] | None = Query(default=None),
    minimum_salary: float | None = Query(default=None, ge=0),
    include_expired: bool = Query(default=False),
    include_deleted: bool = Query(default=False),
):
    session = SessionLocal()

    try:
        repository = JobRepository(session)

        results, total = repository.search_fts(
            query=q,
            limit=limit,
            offset=offset,
            company=company,
            employment_type=employment_type,
            location=location,
            seniority=seniority,
            category=category,
            minimum_salary=minimum_salary,
            include_expired=include_expired,
            include_deleted=include_deleted,
        )

        formatted_jobs = []
        for item in results:
            j = item["job"]
            job_dict = {
                "id": j.id,
                "source": j.source,
                "external_id": j.external_id,
                "title": j.title,
                "excerpt": j.excerpt,
                "company": j.company,
                "company_slug": j.company_slug,
                "company_logo": j.company_logo,
                "employment_type": j.employment_type,
                "minimum_salary": j.minimum_salary,
                "maximum_salary": j.maximum_salary,
                "salary_period": j.salary_period,
                "currency": j.currency,
                "seniority": j.seniority or [],
                "location_restrictions": j.location_restrictions or [],
                "timezone_restrictions": j.timezone_restrictions or [],
                "categories": j.categories or [],
                "parent_categories": j.parent_categories or [],
                "description": j.description,
                "published_at": j.published_at,
                "expires_at": j.expires_at,
                "application_url": j.application_url,
                "source_url": j.source_url,
                "content_hash": j.content_hash,
                "fetched_at": j.fetched_at,
                "created_at": j.created_at,
                "updated_at": j.updated_at,
                "is_deleted": j.is_deleted,
                "deleted_at": j.deleted_at,
                "fts_snippet": item["fts_snippet"],
                "relevance_score": item["relevance_score"],
            }
            formatted_jobs.append(job_dict)

        return {
            "count": len(formatted_jobs),
            "total": total,
            "limit": limit,
            "offset": offset,
            "jobs": formatted_jobs,
        }

    finally:
        session.close()


# =========================================
# GET FILTER OPTIONS / METADATA
# =========================================

@router.get(
    "/filters",
    response_model=FilterOptionsResponse,
)
def get_job_filters():

    session = SessionLocal()

    try:

        repository = JobRepository(
            session
        )

        filters = repository.get_filter_options()

        return filters

    finally:

        session.close()


# =========================================
# GET JOB STATS
#
# Must be BEFORE /{job_id} to prevent
# route shadowing.
# =========================================

@router.get(
    "/stats",
    response_model=JobStatsResponse,
)
def get_job_stats():

    session = SessionLocal()

    try:

        repository = JobRepository(
            session
        )

        return repository.get_job_stats()

    finally:

        session.close()


# =========================================
# GET EXPIRED JOBS
# =========================================

@router.get(
    "/expired",
    response_model=JobListResponse,
)
def get_expired_jobs(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
):

    session = SessionLocal()

    try:

        repository = JobRepository(
            session
        )

        jobs, total = (
            repository.get_expired_jobs(
                limit=limit,
                offset=offset,
            )
        )

        return {
            "count": len(jobs),
            "total": total,
            "limit": limit,
            "offset": offset,
            "jobs": jobs,
        }

    finally:

        session.close()


# =========================================
# GET DELETED JOBS
# =========================================

@router.get(
    "/deleted",
    response_model=JobListResponse,
)
def get_deleted_jobs(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
):

    session = SessionLocal()

    try:

        repository = JobRepository(
            session
        )

        jobs, total = (
            repository.get_deleted_jobs(
                limit=limit,
                offset=offset,
            )
        )

        return {
            "count": len(jobs),
            "total": total,
            "limit": limit,
            "offset": offset,
            "jobs": jobs,
        }

    finally:

        session.close()


# =========================================
# GET SINGLE JOB
# =========================================

@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: int,
):

    session = SessionLocal()

    try:

        repository = JobRepository(
            session
        )

        job = repository.get_by_id(
            job_id
        )

        # =================================
        # NOT FOUND
        # =================================

        if job is None:

            raise HTTPException(
                status_code=404,
                detail="Job not found",
            )

        # =================================
        # RESPONSE
        # =================================

        return job

    finally:

        session.close()


# =========================================
# GET SIMILAR JOBS (RECOMMENDATION ENGINE)
# =========================================

@router.get(
    "/{job_id}/similar",
    response_model=SimilarJobListResponse,
)
def get_similar_jobs(
    job_id: int,
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    min_score: float = Query(
        default=0.1,
        ge=0.0,
        le=1.0,
    ),
):

    session = SessionLocal()

    try:

        repository = JobRepository(session)

        # Check target job exists and is active
        target_job = repository.get_by_id(job_id)

        if target_job is None:

            raise HTTPException(
                status_code=404,
                detail="Job not found",
            )

        jobs, total = RecommendationEngine.get_similar_jobs(
            session=session,
            job_id=job_id,
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

    finally:

        session.close()



# =========================================
# GET JOB CHANGES (LIST)
# =========================================

@router.get(
    "/{job_id}/changes",
    response_model=JobChangeListResponse,
)
def get_job_changes(
    job_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):

    session = SessionLocal()

    try:

        job_repo = JobRepository(session)

        job = job_repo.get_by_id(job_id)

        if job is None:

            raise HTTPException(
                status_code=404,
                detail="Job not found",
            )

        change_repo = JobChangeRepository(session)

        changes, total = change_repo.get_by_job_id_paginated(
            job_id=job_id,
            limit=limit,
            offset=offset,
        )

        return {
            "count": len(changes),
            "total": total,
            "limit": limit,
            "offset": offset,
            "changes": changes,
        }

    finally:

        session.close()


# =========================================
# GET SINGLE JOB CHANGE
# =========================================

@router.get(
    "/{job_id}/changes/{change_id}",
    response_model=JobChangeResponse,
)
def get_job_change_detail(
    job_id: int,
    change_id: int,
):

    session = SessionLocal()

    try:

        job_repo = JobRepository(session)

        job = job_repo.get_by_id(job_id)

        if job is None:

            raise HTTPException(
                status_code=404,
                detail="Job not found",
            )

        change_repo = JobChangeRepository(session)

        change = change_repo.get_by_id(change_id)

        if change is None or change.job_id != job_id:

            raise HTTPException(
                status_code=404,
                detail="Job change record not found",
            )

        return change

    finally:

        session.close()


# =========================================
# SOFT DELETE JOB
# =========================================

@router.delete(
    "/{job_id}",
    response_model=JobResponse,
)
def soft_delete_job(
    job_id: int,
):

    session = SessionLocal()

    try:

        repository = JobRepository(
            session
        )

        job = repository.soft_delete(
            job_id
        )

        if job is None:

            raise HTTPException(
                status_code=404,
                detail="Job not found",
            )

        return job

    finally:

        session.close()


# =========================================
# RESTORE SOFT-DELETED JOB
# =========================================

@router.post(
    "/{job_id}/restore",
    response_model=JobResponse,
)
def restore_job(
    job_id: int,
):

    session = SessionLocal()

    try:

        repository = JobRepository(
            session
        )

        job = repository.restore(
            job_id
        )

        if job is None:

            raise HTTPException(
                status_code=404,
                detail="Job not found",
            )

        return job

    finally:

        session.close()