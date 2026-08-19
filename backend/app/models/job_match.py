from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from app.models.responses import JobResponse


class UserProfileMatchRequest(BaseModel):
    desired_title: Optional[str] = Field(None, max_length=255)
    skills: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    seniority: List[str] = Field(default_factory=list)
    min_salary: Optional[float] = Field(None, ge=0)


class MatchBreakdown(BaseModel):
    title_match: float
    skill_match: float
    location_match: float
    seniority_match: float
    salary_match: float


class MatchedJobResponse(JobResponse):
    match_score: float
    match_breakdown: MatchBreakdown


class MatchedJobListResponse(BaseModel):
    count: int
    total: int
    limit: int
    offset: int
    jobs: List[MatchedJobResponse]


class SingleJobMatchResponse(BaseModel):
    job_id: int
    job_title: str
    match_score: float
    match_breakdown: MatchBreakdown
