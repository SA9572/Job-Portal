from datetime import datetime, timezone

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes.jobs import router as jobs_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.auth import router as auth_router
from app.api.routes.saved_jobs import router as saved_jobs_router
from app.api.routes.job_alerts import router as job_alerts_router
from app.api.routes.matching import router as matching_router
from app.core.logging_config import logger


app = FastAPI(
    title="Job Required API",
    version="1.0.0",
    description="Job ingestion and search API",
)


# =============================================
# EXCEPTION HANDLERS
# =============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):

    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
    }

    code = code_map.get(exc.status_code, "HTTP_ERROR")
    logger.warning("HTTPException [%s] path=%s: %s", exc.status_code, request.url.path, exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": str(exc.detail),
                "status_code": exc.status_code,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    logger.warning("RequestValidationError path=%s: %s", request.url.path, exc.errors())

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "UNPROCESSABLE_ENTITY",
                "message": "Validation error in request parameters",
                "details": exc.errors(),
                "status_code": 422,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):

    logger.error("Unhandled Exception path=%s: %s", request.url.path, str(exc), exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred",
                "status_code": 500,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "job-required-api",
    }


app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"],
)

app.include_router(
    saved_jobs_router,
    prefix="/api/saved-jobs",
    tags=["Saved Jobs"],
)

app.include_router(
    job_alerts_router,
    prefix="/api/alerts",
    tags=["Job Alerts"],
)

app.include_router(
    matching_router,
    prefix="/api/match",
    tags=["Job Matching"],
)

app.include_router(
    jobs_router,
    prefix="/api/jobs",
    tags=["Jobs"],
)

app.include_router(
    ingestion_router,
    prefix="/api/ingestion",
    tags=["Ingestion"],
)