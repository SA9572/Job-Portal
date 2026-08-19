import hashlib
from datetime import datetime, timezone

from app.models.job import Job
from app.services.http_client import ResilientHttpClient
from app.sources.base import JobSource


class RemoteOKSource(JobSource):

    BASE_URL = "https://remoteok.com/api"

    @property
    def source_name(self) -> str:
        return "remoteok"

    def __init__(
        self,
        timeout: float = 20.0,
        http_client: ResilientHttpClient | None = None,
    ):
        self.timeout = timeout
        self.http_client = http_client or ResilientHttpClient(
            timeout=timeout
        )

    def fetch_jobs(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Job]:
        response = self.http_client.get(self.BASE_URL)
        data = response.json()

        # RemoteOK returns array where first element is metadata legal notice
        if isinstance(data, list) and len(data) > 0 and "legal" in data[0]:
            raw_jobs = data[1:]
        elif isinstance(data, list):
            raw_jobs = data
        else:
            raw_jobs = []

        sliced = raw_jobs[offset : offset + limit]

        jobs = []
        for raw_job in sliced:
            if isinstance(raw_job, dict) and "id" in raw_job:
                jobs.append(self._normalize_job(raw_job))

        return jobs

    def fetch_all_jobs(
        self,
        max_pages: int = 5,
        page_size: int = 20,
    ) -> list[Job]:
        all_jobs: list[Job] = []

        for page_number in range(max_pages):
            offset = page_number * page_size
            jobs = self.fetch_jobs(limit=page_size, offset=offset)

            if not jobs:
                break

            all_jobs.extend(jobs)

            if len(jobs) < page_size:
                break

        return all_jobs

    def _normalize_job(self, raw_job: dict) -> Job:
        now = datetime.now(timezone.utc)
        ext_id = str(raw_job.get("id", ""))
        title = raw_job.get("position", "Untitled Position")
        company = raw_job.get("company", "Unknown Company")
        description = raw_job.get("description", "")
        url = raw_job.get("url") or f"https://remoteok.com/remote-jobs/{ext_id}"

        # Calculate content hash
        content = f"{title}|{company}|{description}|{url}"
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # Parse salary
        min_sal = float(raw_job["salary_min"]) if raw_job.get("salary_min") else None
        max_sal = float(raw_job["salary_max"]) if raw_job.get("salary_max") else None

        # Parse tags as categories
        tags = raw_job.get("tags", [])

        # Parse location
        location = [raw_job["location"]] if raw_job.get("location") else []

        return Job(
            source=self.source_name,
            external_id=ext_id,
            title=title,
            excerpt=description[:200] if description else None,
            company=company,
            company_slug=company.lower().replace(" ", "-") if company else None,
            company_logo=raw_job.get("company_logo"),
            employment_type="Full Time",
            minimum_salary=min_sal,
            maximum_salary=max_sal,
            salary_period="year",
            currency="USD",
            seniority=[],
            location_restrictions=location,
            timezone_restrictions=[],
            categories=tags,
            parent_categories=[],
            description=description,
            published_at=now,
            expires_at=None,
            application_url=url,
            source_url=url,
            content_hash=content_hash,
            fetched_at=now,
        )
