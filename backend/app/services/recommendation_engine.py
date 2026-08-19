import re
from datetime import datetime, timezone
from typing import List, Tuple, Set, Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session

from app.database.job_model import JobModel

STOP_WORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below", "to",
    "from", "up", "upon", "down", "in", "out", "on", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "s", "t", "can", "will", "just", "don", "should", "now",
    "job", "remote", "fulltime", "parttime", "work", "hiring", "looking"
}


class RecommendationEngine:
    """
    Content-based job recommendation engine.
    Calculates weighted similarity scores between job postings based on:
    - Title Keyword Overlap (35%)
    - Category & Parent Category Match (25%)
    - Location Restrictions Overlap (15%)
    - Seniority Level Match (15%)
    - Employment Type & Company Match (5%)
    - Salary Range Proximity (5%)
    """

    @staticmethod
    def tokenize(text: Optional[str]) -> Set[str]:
        if not text:
            return set()
        tokens = re.findall(r"\b[a-zA-Z0-9+#.-]{2,}\b", text.lower())
        return {t for t in tokens if t not in STOP_WORDS}

    @staticmethod
    def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return intersection / union if union > 0 else 0.0

    @classmethod
    def calculate_similarity(cls, job_a: JobModel, job_b: JobModel) -> float:
        if job_a.id == job_b.id:
            return 1.0

        # 1. Title Similarity (35%)
        title_a = cls.tokenize(job_a.title)
        title_b = cls.tokenize(job_b.title)
        title_score = cls.jaccard_similarity(title_a, title_b)

        # 2. Category Match (25%)
        cats_a = set(job_a.categories or []) | set(job_a.parent_categories or [])
        cats_b = set(job_b.categories or []) | set(job_b.parent_categories or [])
        cats_a_clean = {c.strip().lower() for c in cats_a if isinstance(c, str)}
        cats_b_clean = {c.strip().lower() for c in cats_b if isinstance(c, str)}
        category_score = cls.jaccard_similarity(cats_a_clean, cats_b_clean)

        # 3. Location Restrictions (15%)
        locs_a = {l.strip().lower() for l in (job_a.location_restrictions or []) if isinstance(l, str)}
        locs_b = {l.strip().lower() for l in (job_b.location_restrictions or []) if isinstance(l, str)}
        if not locs_a and not locs_b:
            location_score = 0.5  # Neutral if both unrestricted
        else:
            location_score = cls.jaccard_similarity(locs_a, locs_b)

        # 4. Seniority Level (15%)
        sen_a = {s.strip().lower() for s in (job_a.seniority or []) if isinstance(s, str)}
        sen_b = {s.strip().lower() for s in (job_b.seniority or []) if isinstance(s, str)}
        if not sen_a and not sen_b:
            seniority_score = 0.5
        else:
            seniority_score = cls.jaccard_similarity(sen_a, sen_b)

        # 5. Employment Type & Company (5%)
        emp_company_score = 0.0
        if job_a.employment_type and job_b.employment_type:
            if job_a.employment_type.lower() == job_b.employment_type.lower():
                emp_company_score += 0.5
        if job_a.company and job_b.company:
            if job_a.company.lower() == job_b.company.lower():
                emp_company_score += 0.5

        # 6. Salary Range Proximity (5%)
        salary_score = 0.0
        if (job_a.minimum_salary or job_a.maximum_salary) and (job_b.minimum_salary or job_b.maximum_salary):
            min_a = job_a.minimum_salary or job_a.maximum_salary or 0
            max_a = job_a.maximum_salary or job_a.minimum_salary or 0
            min_b = job_b.minimum_salary or job_b.maximum_salary or 0
            max_b = job_b.maximum_salary or job_b.minimum_salary or 0

            overlap_start = max(min_a, min_b)
            overlap_end = min(max_a, max_b)
            if overlap_end >= overlap_start:
                range_span = max(max_a, max_b) - min(min_a, min_b)
                if range_span > 0:
                    salary_score = (overlap_end - overlap_start) / range_span
                else:
                    salary_score = 1.0

        total_score = (
            (title_score * 0.35) +
            (category_score * 0.25) +
            (location_score * 0.15) +
            (seniority_score * 0.15) +
            (emp_company_score * 0.05) +
            (salary_score * 0.05)
        )

        return round(total_score, 4)

    @classmethod
    def get_similar_jobs(
        cls,
        session: Session,
        job_id: int,
        limit: int = 10,
        offset: int = 0,
        min_score: float = 0.1,
    ) -> Tuple[List[dict], int]:
        target_job = session.execute(
            select(JobModel).where(
                JobModel.id == job_id,
                JobModel.is_deleted == False,
            )
        ).scalar_one_or_none()

        if target_job is None:
            return [], 0

        now = datetime.now(timezone.utc)

        # Retrieve active candidates (not deleted, not expired, excluding target job)
        candidates_stmt = (
            select(JobModel)
            .where(
                JobModel.id != job_id,
                JobModel.is_deleted == False,
                or_(
                    JobModel.expires_at.is_(None),
                    JobModel.expires_at >= now,
                ),
            )
        )

        candidates = session.execute(candidates_stmt).scalars().all()

        scored_candidates = []
        for candidate in candidates:
            score = cls.calculate_similarity(target_job, candidate)
            if score >= min_score:
                scored_candidates.append((candidate, score))

        # Sort by similarity score descending, then by id descending
        scored_candidates.sort(key=lambda x: (x[1], x[0].id), reverse=True)

        total = len(scored_candidates)
        paginated = scored_candidates[offset : offset + limit]

        results = []
        for job_model, score in paginated:
            # Build dictionary / dict representation with similarity_score attached
            job_dict = {
                "id": job_model.id,
                "source": job_model.source,
                "external_id": job_model.external_id,
                "title": job_model.title,
                "excerpt": job_model.excerpt,
                "company": job_model.company,
                "company_slug": job_model.company_slug,
                "company_logo": job_model.company_logo,
                "employment_type": job_model.employment_type,
                "minimum_salary": job_model.minimum_salary,
                "maximum_salary": job_model.maximum_salary,
                "salary_period": job_model.salary_period,
                "currency": job_model.currency,
                "seniority": job_model.seniority or [],
                "location_restrictions": job_model.location_restrictions or [],
                "timezone_restrictions": job_model.timezone_restrictions or [],
                "categories": job_model.categories or [],
                "parent_categories": job_model.parent_categories or [],
                "description": job_model.description,
                "published_at": job_model.published_at,
                "expires_at": job_model.expires_at,
                "application_url": job_model.application_url,
                "source_url": job_model.source_url,
                "content_hash": job_model.content_hash,
                "fetched_at": job_model.fetched_at,
                "created_at": job_model.created_at,
                "updated_at": job_model.updated_at,
                "is_deleted": job_model.is_deleted,
                "deleted_at": job_model.deleted_at,
                "similarity_score": score,
            }
            results.append(job_dict)

        return results, total
