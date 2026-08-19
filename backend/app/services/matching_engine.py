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
        desired_title = (profile.get("desired_title") or "").strip().lower()
        job_title_lower = (job.title or "").lower()
        job_excerpt_lower = (job.excerpt or "").lower()
        job_full_text = f"{job_title_lower} {job_excerpt_lower}"

        if not desired_title:
            title_score = 0.5
        else:
            # Extract words including 2+ char terms (e.g. ml, ai, go, js, qa)
            title_words = [w for w in re.findall(r"\b[a-zA-Z0-9+#.-]+\b", desired_title) if w not in STOP_WORDS]
            if not title_words:
                title_score = 0.5
            else:
                matches = sum(1 for w in title_words if w in job_full_text)
                title_score = matches / len(title_words)
                # Boost if exact phrase or main title match
                if desired_title in job_title_lower:
                    title_score = 1.0
                elif any(w in job_title_lower for w in title_words):
                    title_score = max(title_score, 0.75)

        # 2. Skill Set Match (30% weight)
        user_skills = [s.strip().lower() for s in (profile.get("skills") or []) if isinstance(s, str) and s.strip()]
        if not user_skills:
            skill_score = 0.5
        else:
            job_categories_lower = [c.strip().lower() for c in (job.categories or []) if isinstance(c, str)]
            job_parents_lower = [c.strip().lower() for c in (job.parent_categories or []) if isinstance(c, str)]
            job_desc_lower = (job.description or "").lower()[:2000]

            matched_count = 0
            for skill in user_skills:
                if (
                    any(skill in c for c in job_categories_lower)
                    or any(skill in p for p in job_parents_lower)
                    or skill in job_title_lower
                    or skill in job_desc_lower
                ):
                    matched_count += 1
            skill_score = matched_count / len(user_skills)

        # 3. Location Preference Match (15% weight)
        user_locations = [l.strip().lower() for l in (profile.get("preferred_locations") or []) if isinstance(l, str)]
        job_locations = [l.strip().lower() for l in (job.location_restrictions or []) if isinstance(l, str)]

        if not user_locations:
            location_score = 0.8
        else:
            is_user_remote = any("remote" in l or "anywhere" in l or "worldwide" in l for l in user_locations)
            is_job_remote = not job_locations or any("remote" in l or "anywhere" in l or "worldwide" in l for l in job_locations)

            if is_user_remote and is_job_remote:
                location_score = 1.0
            else:
                matched_loc = any(
                    any(ul in jl or jl in ul for jl in job_locations)
                    for ul in user_locations
                )
                location_score = 1.0 if matched_loc else 0.2

        # 4. Seniority Level Match (10% weight)
        user_seniority = [s.strip().lower() for s in (profile.get("seniority") or []) if isinstance(s, str)]
        job_seniority = [s.strip().lower() for s in (job.seniority or []) if isinstance(s, str)]

        if not user_seniority:
            seniority_score = 0.8
        elif not job_seniority:
            # Check title for seniority keywords
            title_has_sen = any(sen in job_title_lower for sen in user_seniority)
            seniority_score = 1.0 if title_has_sen else 0.5
        else:
            match_sen = any(us in js for us in user_seniority for js in job_seniority)
            seniority_score = 1.0 if match_sen else 0.3

        # 5. Salary Expectation Match (10% weight)
        min_salary_req = profile.get("min_salary")
        if min_salary_req is None or min_salary_req <= 0:
            salary_score = 0.5
        else:
            job_max = job.maximum_salary or job.minimum_salary or 0

            if job_max >= min_salary_req:
                salary_score = 1.0
            elif job_max > 0:
                salary_score = round(max(0.2, job_max / min_salary_req), 2)
            else:
                salary_score = 0.4  # unlisted salary default

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
