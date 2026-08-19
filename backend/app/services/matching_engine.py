import re
from datetime import datetime, timezone
from typing import List, Tuple, Set, Dict, Any, Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.database.job_model import JobModel
from app.services.recommendation_engine import RecommendationEngine, STOP_WORDS


class JobMatchingEngine:
    """
    Personalized Job Matching Engine.
    Evaluates candidate user profiles (skills, title preferences, location, seniority, salary expectations)
    against active job postings, computing a multi-factor match score and detailed breakdown.
    """

    @classmethod
    def calculate_user_match(cls, profile: dict, job: JobModel) -> Tuple[float, dict]:
        """
        Calculates match score between user profile dict and JobModel instance.
        Returns (total_score: float, breakdown: dict).
        """

        # 1. Title & Keyword Match (35% weight)
        desired_title = profile.get("desired_title") or ""
        title_tokens = RecommendationEngine.tokenize(desired_title)
        job_title_tokens = RecommendationEngine.tokenize(job.title)
        job_excerpt_tokens = RecommendationEngine.tokenize(job.excerpt)
        job_combined = job_title_tokens | job_excerpt_tokens

        title_score = RecommendationEngine.jaccard_similarity(title_tokens, job_combined) if title_tokens else 0.5

        # 2. Skill Set Match (30% weight)
        user_skills = {s.strip().lower() for s in (profile.get("skills") or []) if isinstance(s, str)}
        job_categories = {c.strip().lower() for c in (job.categories or []) if isinstance(c, str)}
        job_parents = {c.strip().lower() for c in (job.parent_categories or []) if isinstance(c, str)}
        job_desc_tokens = RecommendationEngine.tokenize(job.description[:1000])  # sample description keywords
        job_skills = job_categories | job_parents | job_desc_tokens

        if not user_skills:
            skill_score = 0.5
        else:
            intersection = len(user_skills.intersection(job_skills))
            skill_score = intersection / len(user_skills) if len(user_skills) > 0 else 0.0
            skill_score = min(skill_score, 1.0)

        # 3. Location Preference Match (15% weight)
        user_locations = {l.strip().lower() for l in (profile.get("preferred_locations") or []) if isinstance(l, str)}
        job_locations = {l.strip().lower() for l in (job.location_restrictions or []) if isinstance(l, str)}

        if not user_locations and not job_locations:
            location_score = 1.0
        elif not user_locations or not job_locations:
            location_score = 0.7  # neutral-high match if flexible
        else:
            # Check overlap or remote matches
            if user_locations.intersection(job_locations) or ("remote" in user_locations and "remote" in job_locations):
                location_score = 1.0
            else:
                location_score = 0.2

        # 4. Seniority Level Match (10% weight)
        user_seniority = {s.strip().lower() for s in (profile.get("seniority") or []) if isinstance(s, str)}
        job_seniority = {s.strip().lower() for s in (job.seniority or []) if isinstance(s, str)}

        if not user_seniority or not job_seniority:
            seniority_score = 0.5
        else:
            seniority_score = 1.0 if user_seniority.intersection(job_seniority) else 0.2

        # 5. Salary Expectation Match (10% weight)
        min_salary_req = profile.get("min_salary")
        if min_salary_req is None or min_salary_req <= 0:
            salary_score = 0.5
        else:
            job_max = job.maximum_salary or job.minimum_salary or 0
            job_min = job.minimum_salary or job.maximum_salary or 0

            if job_max >= min_salary_req:
                salary_score = 1.0
            elif job_min > 0:
                salary_score = round(max(0.0, job_max / min_salary_req), 2)
            else:
                salary_score = 0.5

        total_score = (
            (title_score * 0.35) +
            (skill_score * 0.30) +
            (location_score * 0.15) +
            (seniority_score * 0.10) +
            (salary_score * 0.10)
        )

        total_score_rounded = round(total_score, 4)

        breakdown = {
            "title_match": round(title_score, 4),
            "skill_match": round(skill_score, 4),
            "location_match": round(location_score, 4),
            "seniority_match": round(seniority_score, 4),
            "salary_match": round(salary_score, 4),
        }

        return total_score_rounded, breakdown

    @classmethod
    def match_jobs_for_user(
        cls,
        session: Session,
        profile: dict,
        limit: int = 10,
        offset: int = 0,
        min_score: float = 0.1,
    ) -> Tuple[List[dict], int]:
        now = datetime.now(timezone.utc)

        # Retrieve active jobs
        stmt = (
            select(JobModel)
            .where(
                JobModel.is_deleted == False,
                or_(
                    JobModel.expires_at.is_(None),
                    JobModel.expires_at >= now,
                ),
            )
        )

        candidates = session.execute(stmt).scalars().all()

        results = []
        for candidate in candidates:
            score, breakdown = cls.calculate_user_match(profile, candidate)
            if score >= min_score:
                job_dict = {
                    "id": candidate.id,
                    "source": candidate.source,
                    "external_id": candidate.external_id,
                    "title": candidate.title,
                    "excerpt": candidate.excerpt,
                    "company": candidate.company,
                    "company_slug": candidate.company_slug,
                    "company_logo": candidate.company_logo,
                    "employment_type": candidate.employment_type,
                    "minimum_salary": candidate.minimum_salary,
                    "maximum_salary": candidate.maximum_salary,
                    "salary_period": candidate.salary_period,
                    "currency": candidate.currency,
                    "seniority": candidate.seniority or [],
                    "location_restrictions": candidate.location_restrictions or [],
                    "timezone_restrictions": candidate.timezone_restrictions or [],
                    "categories": candidate.categories or [],
                    "parent_categories": candidate.parent_categories or [],
                    "description": candidate.description,
                    "published_at": candidate.published_at,
                    "expires_at": candidate.expires_at,
                    "application_url": candidate.application_url,
                    "source_url": candidate.source_url,
                    "content_hash": candidate.content_hash,
                    "fetched_at": candidate.fetched_at,
                    "created_at": candidate.created_at,
                    "updated_at": candidate.updated_at,
                    "is_deleted": candidate.is_deleted,
                    "deleted_at": candidate.deleted_at,
                    "match_score": score,
                    "match_breakdown": breakdown,
                }
                results.append((job_dict, score, candidate.id))

        results.sort(key=lambda x: (x[1], x[2]), reverse=True)

        total = len(results)
        paginated = results[offset : offset + limit]

        matched_jobs = [r[0] for r in paginated]
        return matched_jobs, total
