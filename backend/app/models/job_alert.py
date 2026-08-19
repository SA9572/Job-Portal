from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.responses import JobResponse


class JobAlertCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    keywords: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=255)
    seniority: Optional[str] = Field(None, max_length=255)
    min_salary: Optional[float] = Field(None, ge=0)
    frequency: str = Field("daily", max_length=50)
    is_active: bool = True


class JobAlertUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    keywords: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=255)
    seniority: Optional[str] = Field(None, max_length=255)
    min_salary: Optional[float] = Field(None, ge=0)
    frequency: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class JobAlertResponse(BaseModel):
    id: int
    user_id: int
    name: str
    keywords: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    seniority: Optional[str] = None
    min_salary: Optional[float] = None
    frequency: str
    is_active: bool
    last_sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class JobAlertListResponse(BaseModel):
    count: int
    total: int
    limit: int
    offset: int
    alerts: List[JobAlertResponse]


class AlertMatchResponse(BaseModel):
    alert_id: int
    alert_name: str
    count: int
    total: int
    jobs: List[JobResponse]
