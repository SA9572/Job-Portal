from datetime import datetime, timezone

from sqlalchemy import (
    String,
    and_,
    cast,
    func,
    or_,
    select,
    text,
)

from sqlalchemy.orm import Session

from app.database.job_model import JobModel
from app.models.job import Job


# =============================================
# ALLOWED SORT FIELDS
#
# Whitelist of column names that may be
# used in sort_by to prevent SQL injection.
# =============================================

ALLOWED_SORT_FIELDS: dict[str, str] = {
    "id": "id",
    "title": "title",
    "company": "company",
    "minimum_salary": "minimum_salary",
    "maximum_salary": "maximum_salary",
    "published_at": "published_at",
    "created_at": "created_at",
    "updated_at": "updated_at",
}

# Legacy sort_by aliases for backward
# compatibility with existing callers.

LEGACY_SORT_ALIASES: dict[
    str,
    tuple[str, str],
] = {
    "salary_high": (
        "maximum_salary",
        "desc",
    ),
    "salary_low": (
        "minimum_salary",
        "asc",
    ),
    "newest": (
        "published_at",
        "desc",
    ),
    "oldest": (
        "published_at",
        "asc",
    ),
}


class JobRepository:

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    # =========================================
    # GET JOB BY SOURCE + EXTERNAL ID
    # =========================================

    def get_by_identity(
        self,
        source: str,
        external_id: str,
    ) -> JobModel | None:

        statement = (
            select(JobModel)
            .where(
                JobModel.source == source,
                JobModel.external_id == external_id,
            )
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    # =========================================
    # GET JOB BY DATABASE ID
    # =========================================

    def get_by_id(
        self,
        job_id: int,
        include_deleted: bool = False,
    ) -> JobModel | None:

        statement = (
            select(JobModel)
            .where(
                JobModel.id == job_id
            )
        )

        if not include_deleted:
            statement = statement.where(
                JobModel.is_deleted == False
            )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    # =========================================
    # GET JOBS
    #
    # SEARCH + FILTER + PAGINATION
    # + MULTIPLE VALUES
    # =========================================

    def get_jobs(
        self,
        limit: int = 20,
        offset: int = 0,

        search: str | None = None,

        company: list[str] | None = None,

        employment_type: list[str] | None = None,

        location: list[str] | None = None,

        seniority: list[str] | None = None,

        category: list[str] | None = None,

        minimum_salary: float | None = None,

        sort_by: str | None = None,

        sort_order: str | None = None,

        include_expired: bool = False,

        include_deleted: bool = False,
    ) -> tuple[list[JobModel], int]:

        # =====================================
        # NORMALIZE FILTERS
        #
        # Accept both str and list[str]
        # "India" → ["India"]
        # ["India", "US"] → ["India", "US"]
        # None → None
        # =====================================

        company = self._normalize_filter(
            company
        )

        employment_type = self._normalize_filter(
            employment_type
        )

        location = self._normalize_filter(
            location
        )

        seniority = self._normalize_filter(
            seniority
        )

        category = self._normalize_filter(
            category
        )

        # =====================================
        # BASE QUERY
        # =====================================

        statement = select(
            JobModel
        )

        # =====================================
        # ACTIVE FILTERING
        #
        # By default, exclude deleted and
        # expired jobs for public consumers.
        # =====================================

        if not include_deleted:
            statement = statement.where(
                JobModel.is_deleted == False
            )

        if not include_expired:
            now = datetime.now(timezone.utc)
            statement = statement.where(
                or_(
                    JobModel.expires_at.is_(None),
                    JobModel.expires_at >= now,
                )
            )

        # =====================================
        # SEARCH
        # =====================================

        if search:

            search_value = (
                f"%{search.strip().lower()}%"
            )

            statement = statement.where(
                or_(
                    func.lower(
                        JobModel.title
                    ).like(search_value),

                    func.lower(
                        JobModel.company
                    ).like(search_value),

                    func.lower(
                        JobModel.excerpt
                    ).like(search_value),

                    func.lower(
                        JobModel.description
                    ).like(search_value),
                )
            )

        # =====================================
        # COMPANY
        #
        # Multiple values = OR
        # =====================================

        if company:

            company_conditions = []

            for value in company:

                value = value.strip()

                if value:

                    company_conditions.append(
                        func.lower(
                            JobModel.company
                        ).like(
                            f"%{value.lower()}%"
                        )
                    )

            if company_conditions:

                statement = statement.where(
                    or_(
                        *company_conditions
                    )
                )

        # =====================================
        # EMPLOYMENT TYPE
        #
        # Multiple values = OR
        # =====================================

        if employment_type:

            employment_conditions = []

            for value in employment_type:

                value = value.strip()

                if value:

                    employment_conditions.append(
                        func.lower(
                            JobModel.employment_type
                        ).like(
                            f"%{value.lower()}%"
                        )
                    )

            if employment_conditions:

                statement = statement.where(
                    or_(
                        *employment_conditions
                    )
                )

        # =====================================
        # LOCATION
        #
        # JSON ARRAY
        #
        # Multiple values = OR
        # =====================================

        if location:
            location_conditions = []
            for value in location:
                value = value.strip()
                if value:
                    location_conditions.append(
                        func.lower(cast(JobModel.location_restrictions, String)).like(f"%{value.lower()}%")
                    )
            if location_conditions:
                statement = statement.where(or_(*location_conditions))

        # =====================================
        # SENIORITY
        # =====================================

        if seniority:
            seniority_conditions = []
            for value in seniority:
                value = value.strip()
                if value:
                    seniority_conditions.append(
                        func.lower(cast(JobModel.seniority, String)).like(f"%{value.lower()}%")
                    )
            if seniority_conditions:
                statement = statement.where(or_(*seniority_conditions))

        # =====================================
        # CATEGORY
        # =====================================

        if category:
            category_conditions = []
            for value in category:
                value = value.strip()
                if value:
                    category_conditions.append(
                        func.lower(cast(JobModel.categories, String)).like(f"%{value.lower()}%")
                    )
            if category_conditions:
                statement = statement.where(or_(*category_conditions))

        # =====================================
        # MINIMUM SALARY
        #
        # Job maximum salary must be >=
        # requested minimum salary
        # =====================================

        if minimum_salary is not None:

            statement = statement.where(
                JobModel.maximum_salary >=
                minimum_salary
            )

        # =====================================
        # SORTING
        # =====================================

        resolved_field = None
        resolved_order = "desc"

        if sort_by is not None:

            # ---------------------------------
            # LEGACY ALIASES
            # ---------------------------------

            if sort_by in LEGACY_SORT_ALIASES:

                resolved_field, resolved_order = (
                    LEGACY_SORT_ALIASES[sort_by]
                )

            # ---------------------------------
            # WHITELISTED FIELD NAMES
            # ---------------------------------

            elif sort_by in ALLOWED_SORT_FIELDS:

                resolved_field = (
                    ALLOWED_SORT_FIELDS[sort_by]
                )

            else:

                raise ValueError(
                    f"Invalid sort_by field: "
                    f"'{sort_by}'. "
                    f"Allowed fields: "
                    f"{', '.join(sorted(ALLOWED_SORT_FIELDS.keys()))}"
                )

        # ---------------------------------
        # SORT ORDER OVERRIDE
        # ---------------------------------

        if sort_order is not None:

            sort_order_lower = (
                sort_order.strip().lower()
            )

            if sort_order_lower not in (
                "asc",
                "desc",
            ):

                raise ValueError(
                    f"Invalid sort_order: "
                    f"'{sort_order}'. "
                    f"Allowed values: "
                    f"asc, desc"
                )

            resolved_order = sort_order_lower

        # ---------------------------------
        # APPLY SORT
        # ---------------------------------

        if resolved_field is not None:

            column = getattr(
                JobModel,
                resolved_field,
            )

            if resolved_order == "asc":

                statement = statement.order_by(
                    column.asc()
                )

            else:

                statement = statement.order_by(
                    column.desc()
                )

        else:

            statement = statement.order_by(
                JobModel.id.desc()
            )

        # =====================================
        # TOTAL COUNT
        # =====================================

        count_statement = (
            select(
                func.count()
            )
            .select_from(
                statement.order_by(None)
                .subquery()
            )
        )

        total = self.session.execute(
            count_statement
        ).scalar_one()

        # =====================================
        # PAGINATION
        # =====================================

        statement = (
            statement
            .offset(offset)
            .limit(limit)
        )

        jobs = list(
            self.session.execute(
                statement
            ).scalars().all()
        )

        return jobs, total

    # =========================================
    # CREATE JOB
    # =========================================

    def create(
        self,
        job: Job,
    ) -> JobModel:

        job_model = self._to_model(
            job
        )

        self.session.add(
            job_model
        )

        self.session.commit()

        self.session.refresh(
            job_model
        )

        return job_model

    # =========================================
    # UPDATE JOB
    # =========================================

    def update(
        self,
        existing: JobModel,
        job: Job,
    ) -> JobModel:

        self._update_model(
            existing,
            job,
        )

        existing.updated_at = (
            datetime.now(
                timezone.utc
            )
        )

        self.session.commit()

        self.session.refresh(
            existing
        )

        return existing

    # =========================================
    # CONVERT PYDANTIC JOB
    # → DATABASE MODEL
    # =========================================

    def _to_model(
        self,
        job: Job,
    ) -> JobModel:

        now = datetime.now(
            timezone.utc
        )

        return JobModel(

            source=job.source,

            external_id=job.external_id,

            title=job.title,

            excerpt=job.excerpt,

            company=job.company,

            company_slug=job.company_slug,

            company_logo=job.company_logo,

            employment_type=(
                job.employment_type
            ),

            minimum_salary=(
                job.minimum_salary
            ),

            maximum_salary=(
                job.maximum_salary
            ),

            salary_period=(
                job.salary_period
            ),

            currency=job.currency,

            seniority=job.seniority,

            location_restrictions=(
                job.location_restrictions
            ),

            timezone_restrictions=(
                job.timezone_restrictions
            ),

            categories=job.categories,

            parent_categories=(
                job.parent_categories
            ),

            description=job.description,

            published_at=(
                job.published_at
            ),

            expires_at=(
                job.expires_at
            ),

            application_url=str(
                job.application_url
            ),

            source_url=str(
                job.source_url
            ),

            content_hash=(
                job.content_hash
            ),

            fetched_at=(
                job.fetched_at
            ),

            created_at=now,

            updated_at=now,
        )

    # =========================================
    # UPDATE DATABASE MODEL
    # =========================================

    def _update_model(
        self,
        existing: JobModel,
        job: Job,
    ) -> None:

        existing.title = job.title

        existing.excerpt = (
            job.excerpt
        )

        existing.company = (
            job.company
        )

        existing.company_slug = (
            job.company_slug
        )

        existing.company_logo = (
            job.company_logo
        )

        existing.employment_type = (
            job.employment_type
        )

        existing.minimum_salary = (
            job.minimum_salary
        )

        existing.maximum_salary = (
            job.maximum_salary
        )

        existing.salary_period = (
            job.salary_period
        )

        existing.currency = (
            job.currency
        )

        existing.seniority = (
            job.seniority
        )

        existing.location_restrictions = (
            job.location_restrictions
        )

        existing.timezone_restrictions = (
            job.timezone_restrictions
        )

        existing.categories = (
            job.categories
        )

        existing.parent_categories = (
            job.parent_categories
        )

        existing.description = (
            job.description
        )

        existing.published_at = (
            job.published_at
        )

        existing.expires_at = (
            job.expires_at
        )

        existing.application_url = str(
            job.application_url
        )

        existing.source_url = str(
            job.source_url
        )

        existing.content_hash = (
            job.content_hash
        )

        existing.fetched_at = (
            job.fetched_at
        )

    # =========================================
    # SOFT DELETE
    # =========================================

    def soft_delete(
        self,
        job_id: int,
    ) -> JobModel | None:

        job = self.get_by_id(
            job_id,
            include_deleted=True,
        )

        if job is None:
            return None

        job.is_deleted = True
        job.deleted_at = datetime.now(
            timezone.utc
        )

        self.session.commit()
        self.session.refresh(job)

        return job

    # =========================================
    # RESTORE SOFT-DELETED JOB
    # =========================================

    def restore(
        self,
        job_id: int,
    ) -> JobModel | None:

        job = self.get_by_id(
            job_id,
            include_deleted=True,
        )

        if job is None:
            return None

        job.is_deleted = False
        job.deleted_at = None

        self.session.commit()
        self.session.refresh(job)

        return job

    # =========================================
    # GET EXPIRED JOBS
    # =========================================

    def get_expired_jobs(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[JobModel], int]:

        now = datetime.now(timezone.utc)

        statement = (
            select(JobModel)
            .where(
                JobModel.is_deleted == False,
                JobModel.expires_at.isnot(None),
                JobModel.expires_at < now,
            )
            .order_by(
                JobModel.expires_at.desc()
            )
        )

        count_statement = (
            select(func.count())
            .select_from(
                statement.order_by(None)
                .subquery()
            )
        )

        total = self.session.execute(
            count_statement
        ).scalar_one()

        statement = (
            statement
            .offset(offset)
            .limit(limit)
        )

        jobs = list(
            self.session.execute(
                statement
            ).scalars().all()
        )

        return jobs, total

    # =========================================
    # GET DELETED JOBS
    # =========================================

    def get_deleted_jobs(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[JobModel], int]:

        statement = (
            select(JobModel)
            .where(
                JobModel.is_deleted == True,
            )
            .order_by(
                JobModel.deleted_at.desc()
            )
        )

        count_statement = (
            select(func.count())
            .select_from(
                statement.order_by(None)
                .subquery()
            )
        )

        total = self.session.execute(
            count_statement
        ).scalar_one()

        statement = (
            statement
            .offset(offset)
            .limit(limit)
        )

        jobs = list(
            self.session.execute(
                statement
            ).scalars().all()
        )

        return jobs, total

    # =========================================
    # JOB STATS
    #
    # Returns counts of active, expired,
    # and deleted jobs.
    # =========================================

    def get_job_stats(self) -> dict:

        now = datetime.now(timezone.utc)

        total = self.session.execute(
            select(func.count(JobModel.id))
        ).scalar_one()

        deleted = self.session.execute(
            select(func.count(JobModel.id))
            .where(
                JobModel.is_deleted == True
            )
        ).scalar_one()

        expired = self.session.execute(
            select(func.count(JobModel.id))
            .where(
                JobModel.is_deleted == False,
                JobModel.expires_at.isnot(None),
                JobModel.expires_at < now,
            )
        ).scalar_one()

        active = total - deleted - expired

        return {
            "total": total,
            "active": active,
            "expired": expired,
            "deleted": deleted,
        }

    # =========================================
    # NORMALIZE FILTER INPUT
    #
    # Accepts str, list[str], or None.
    # Ensures iteration always works
    # correctly over complete values.
    # =========================================

    @staticmethod
    def _normalize_filter(
        value: str | list[str] | None,
    ) -> list[str] | None:

        if value is None:
            return None

        if isinstance(value, str):
            return [value]

        return value

    # =========================================
    # GET FILTER OPTIONS / METADATA
    #
    # Dynamically extracts distinct filter
    # values and min/max salary bounds.
    # =========================================

    def get_filter_options(self) -> dict:

        # -------------------------------------
        # BASE FILTER: only active jobs
        # (not deleted, not expired)
        # -------------------------------------

        now = datetime.now(timezone.utc)

        active_filter = and_(
            JobModel.is_deleted == False,
            or_(
                JobModel.expires_at.is_(None),
                JobModel.expires_at >= now,
            ),
        )

        # -------------------------------------
        # DISTINCT SIMPLE FIELDS
        # -------------------------------------

        companies_stmt = (
            select(func.distinct(JobModel.company))
            .where(
                JobModel.company.isnot(None),
                active_filter,
            )
            .order_by(JobModel.company.asc())
        )

        companies = [
            r for r in self.session.scalars(companies_stmt).all() if r
        ]

        employment_types_stmt = (
            select(func.distinct(JobModel.employment_type))
            .where(
                JobModel.employment_type.isnot(None),
                active_filter,
            )
            .order_by(JobModel.employment_type.asc())
        )

        employment_types = [
            r for r in self.session.scalars(employment_types_stmt).all() if r
        ]

        currencies_stmt = (
            select(func.distinct(JobModel.currency))
            .where(
                JobModel.currency.isnot(None),
                active_filter,
            )
            .order_by(JobModel.currency.asc())
        )

        currencies = [
            r for r in self.session.scalars(currencies_stmt).all() if r
        ]

        # -------------------------------------
        # JSON ARRAY FIELDS (EXTRACT DISTINCT)
        # -------------------------------------

        all_jobs = self.session.scalars(
            select(JobModel)
            .where(active_filter)
        ).all()

        locations_set: set[str] = set()
        seniorities_set: set[str] = set()
        categories_set: set[str] = set()

        for job in all_jobs:

            if job.location_restrictions and isinstance(job.location_restrictions, list):
                for item in job.location_restrictions:
                    if item and isinstance(item, str):
                        locations_set.add(item.strip())

            if job.seniority and isinstance(job.seniority, list):
                for item in job.seniority:
                    if item and isinstance(item, str):
                        seniorities_set.add(item.strip())

            if job.categories and isinstance(job.categories, list):
                for item in job.categories:
                    if item and isinstance(item, str):
                        categories_set.add(item.strip())

        # -------------------------------------
        # SALARY RANGE (MIN & MAX)
        # -------------------------------------

        salary_stmt = (
            select(
                func.min(JobModel.minimum_salary),
                func.max(JobModel.maximum_salary),
            )
            .where(active_filter)
        )

        min_sal, max_sal = self.session.execute(salary_stmt).one()

        return {
            "companies": companies,
            "employment_types": employment_types,
            "locations": sorted(locations_set),
            "seniorities": sorted(seniorities_set),
            "categories": sorted(categories_set),
            "currencies": currencies,
            "min_salary": min_sal,
            "max_salary": max_sal,
        }

    # =========================================
    # FTS5 FULL-TEXT SEARCH & RELEVANCE
    # =========================================

    def search_fts(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        company: list[str] | None = None,
        employment_type: list[str] | None = None,
        location: list[str] | None = None,
        seniority: list[str] | None = None,
        category: list[str] | None = None,
        minimum_salary: float | None = None,
        include_expired: bool = False,
        include_deleted: bool = False,
    ) -> tuple[list[dict], int]:
        if not query or not query.strip():
            jobs, total = self.get_jobs(
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
            return [{"job": j, "fts_snippet": None, "relevance_score": None} for j in jobs], total

        company = self._normalize_filter(company)
        employment_type = self._normalize_filter(employment_type)
        location = self._normalize_filter(location)
        seniority = self._normalize_filter(seniority)
        category = self._normalize_filter(category)

        # Prepare FTS match expression
        raw_terms = [t.strip() for t in query.split() if t.strip()]
        if not raw_terms:
            return [], 0

        # Construct sanitized FTS search query (support wildcards/phrases)
        clean_terms = []
        for term in raw_terms:
            t_clean = term.replace('"', '').replace("'", '').strip()
            if not t_clean:
                continue
            if t_clean.upper() in ["AND", "OR", "NOT"]:
                clean_terms.append(t_clean.upper())
            elif t_clean.endswith("*"):
                clean_terms.append(f"{t_clean[:-1]}*")
            else:
                clean_terms.append(f"{t_clean}*")

        fts_match_query = " ".join(clean_terms)

        # Build SQL query with FTS join
        sql_conditions = ["jobs_fts MATCH :fts_query"]
        params = {"fts_query": fts_match_query, "limit": limit, "offset": offset}

        if not include_deleted:
            sql_conditions.append("jobs.is_deleted = 0")

        if not include_expired:
            sql_conditions.append("(jobs.expires_at IS NULL OR jobs.expires_at >= :now)")
            params["now"] = datetime.now(timezone.utc).isoformat()

        if company:
            comp_conds = []
            for idx, comp in enumerate(company):
                param_key = f"comp_{idx}"
                comp_conds.append(f"LOWER(jobs.company) LIKE :{param_key}")
                params[param_key] = f"%{comp.strip().lower()}%"
            sql_conditions.append(f"({' OR '.join(comp_conds)})")

        if employment_type:
            emp_conds = []
            for idx, emp in enumerate(employment_type):
                param_key = f"emp_{idx}"
                emp_conds.append(f"LOWER(jobs.employment_type) LIKE :{param_key}")
                params[param_key] = f"%{emp.strip().lower()}%"
            sql_conditions.append(f"({' OR '.join(emp_conds)})")

        if location:
            loc_conds = []
            for idx, loc in enumerate(location):
                param_key = f"loc_{idx}"
                loc_conds.append(f"jobs.location_restrictions LIKE :{param_key}")
                params[param_key] = f'%"{loc.strip()}"%'
            sql_conditions.append(f"({' OR '.join(loc_conds)})")

        if seniority:
            sen_conds = []
            for idx, sen in enumerate(seniority):
                param_key = f"sen_{idx}"
                sen_conds.append(f"jobs.seniority LIKE :{param_key}")
                params[param_key] = f'%"{sen.strip()}"%'
            sql_conditions.append(f"({' OR '.join(sen_conds)})")

        if category:
            cat_conds = []
            for idx, cat in enumerate(category):
                param_key = f"cat_{idx}"
                cat_conds.append(f"jobs.categories LIKE :{param_key}")
                params[param_key] = f'%"{cat.strip()}"%'
            sql_conditions.append(f"({' OR '.join(cat_conds)})")

        if minimum_salary is not None:
            sql_conditions.append("jobs.maximum_salary >= :min_sal")
            params["min_sal"] = minimum_salary

        where_clause = " AND ".join(sql_conditions)

        count_sql = f"""
            SELECT COUNT(*)
            FROM jobs
            JOIN jobs_fts ON jobs.id = jobs_fts.rowid
            WHERE {where_clause}
        """

        select_sql = f"""
            SELECT
                jobs.id AS job_id,
                bm25(jobs_fts) AS rank_score,
                snippet(jobs_fts, -1, '<mark>', '</mark>', '...', 15) AS match_snippet
            FROM jobs
            JOIN jobs_fts ON jobs.id = jobs_fts.rowid
            WHERE {where_clause}
            ORDER BY bm25(jobs_fts) ASC, jobs.id DESC
            LIMIT :limit OFFSET :offset
        """

        try:
            total = self.session.execute(text(count_sql), params).scalar() or 0
            rows = self.session.execute(text(select_sql), params).all()
        except Exception:
            # Fallback to standard LIKE search if FTS query syntax error
            jobs, total = self.get_jobs(
                search=query,
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
            return [{"job": j, "fts_snippet": None, "relevance_score": None} for j in jobs], total

        results = []
        for r in rows:
            job_obj = self.get_by_id(r.job_id, include_deleted=include_deleted)
            if job_obj:
                # bm25 in sqlite returns lower (more negative/smaller) value for higher relevance
                relevance = round(abs(float(r.rank_score)), 4) if r.rank_score is not None else 1.0
                results.append({
                    "job": job_obj,
                    "fts_snippet": r.match_snippet,
                    "relevance_score": relevance,
                })

        return results, total