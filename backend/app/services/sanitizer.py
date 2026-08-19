import re
import html
from app.models.job import Job


class DataSanitizer:

    @staticmethod
    def clean_text(text: str | None) -> str | None:
        if text is None:
            return None

        # Decode HTML entities (&amp; -> &, &lt; -> <, etc.)
        cleaned = html.unescape(text)

        # Strip non-printable / control characters except standard whitespace
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)

        # Normalize multiple spaces/newlines
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)

        return cleaned.strip() or None

    @staticmethod
    def strip_html_tags(text: str | None) -> str | None:
        if text is None:
            return None

        # Remove HTML tags (<p>, <div>, <script>, etc.)
        clean_text = re.sub(r"<[^>]*>", " ", text)
        return DataSanitizer.clean_text(clean_text)

    @staticmethod
    def clean_url(url: str | None) -> str | None:
        if url is None:
            return None

        cleaned = str(url).strip()
        if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
            return None

        return cleaned

    @staticmethod
    def clean_list(items: list | None) -> list:
        if not items or not isinstance(items, list):
            return []

        cleaned = []
        for item in items:
            if isinstance(item, str):
                c = DataSanitizer.clean_text(item)
                if c:
                    cleaned.append(c)
            elif item is not None:
                cleaned.append(item)

        return cleaned

    @classmethod
    def sanitize(cls, job: Job) -> Job:
        """Sanitize and clean all fields on a normalized Job instance."""
        # Sanitize Title & Excerpt
        clean_title = cls.clean_text(cls.strip_html_tags(job.title)) or job.title
        clean_excerpt = cls.strip_html_tags(job.excerpt)

        # Sanitize Company
        clean_company = cls.clean_text(cls.strip_html_tags(job.company)) or job.company

        # Sanitize Description (keep structure, unescape html)
        clean_desc = cls.clean_text(job.description) or job.description

        # Sanitize URLs
        clean_app_url = cls.clean_url(job.application_url) or job.application_url
        clean_src_url = cls.clean_url(job.source_url) or job.source_url

        # Sanitize Salaries
        min_sal = job.minimum_salary
        max_sal = job.maximum_salary

        if min_sal is not None and min_sal < 0:
            min_sal = None
        if max_sal is not None and max_sal < 0:
            max_sal = None

        if min_sal is not None and max_sal is not None and min_sal > max_sal:
            min_sal, max_sal = max_sal, min_sal

        # Sanitize List Fields
        clean_seniority = cls.clean_list(job.seniority)
        clean_locations = cls.clean_list(job.location_restrictions)
        clean_timezones = cls.clean_list(job.timezone_restrictions)
        clean_categories = cls.clean_list(job.categories)
        clean_parents = cls.clean_list(job.parent_categories)

        return Job(
            source=job.source,
            external_id=job.external_id,
            title=clean_title,
            excerpt=clean_excerpt,
            company=clean_company,
            company_slug=job.company_slug,
            company_logo=cls.clean_url(job.company_logo),
            employment_type=cls.clean_text(job.employment_type),
            minimum_salary=min_sal,
            maximum_salary=max_sal,
            salary_period=job.salary_period,
            currency=job.currency,
            seniority=clean_seniority,
            location_restrictions=clean_locations,
            timezone_restrictions=clean_timezones,
            categories=clean_categories,
            parent_categories=clean_parents,
            description=clean_desc,
            published_at=job.published_at,
            expires_at=job.expires_at,
            application_url=clean_app_url,
            source_url=clean_src_url,
            content_hash=job.content_hash,
            fetched_at=job.fetched_at,
        )
