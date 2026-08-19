from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.responses import JobResponse


class SaveJobRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=1000)


class SaveStatusResponse(BaseModel):
    job_id: int
    is_saved: bool


class SavedJobResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    notes: Optional[str] = None
    created_at: datetime
    job: JobResponse

    model_config = {
        "from_attributes": True,
    }


class SavedJobListResponse(BaseModel):
    count: int
    total: int
    limit: int
    offset: int
    jobs: List[SavedJobResponse]
