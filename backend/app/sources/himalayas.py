import hashlib
from datetime import datetime, timezone

from app.models.job import Job
from app.services.http_client import ResilientHttpClient
from app.sources.base import JobSource


class HimalayasSource(JobSource):

    BASE_URL = "https://himalayas.app/jobs/api"

    @property
    def source_name(self) -> str:
        return "himalayas"

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

        params = {
            "limit": limit,
            "offset": offset,
        }

        response = self.http_client.get(
            self.BASE_URL,
            params=params,
        )

        data = response.json()

        jobs = []

        for raw_job in data.get("jobs", []):
            job = self._normalize_job(raw_job)
            jobs.append(job)

        return jobs

    def fetch_all_jobs(
        self,
        max_pages: int = 5,
        page_size: int = 20,
    ) -> list[Job]:

        all_jobs: list[Job] = []

        for page_number in range(max_pages):

            offset = page_number * page_size

            jobs = self.fetch_jobs(
                limit=page_size,
                offset=offset,
            )

            if not jobs:
                break

            all_jobs.extend(jobs)

            if len(jobs) < page_size:
                break

        return all_jobs

    def _normalize_job(
        self,
        raw_job: dict,
    ) -> Job:

        now = datetime.now(timezone.utc)

        published_at = self._timestamp_to_datetime(
            raw_job.get("pubDate")
        )

        expires_at = self._timestamp_to_datetime(
            raw_job.get("expiryDate")
        )

        content_hash = self._create_content_hash(
            raw_job
        )

        return Job(
            source="himalayas",
            external_id=raw_job["guid"],

            title=raw_job["title"],
            excerpt=raw_job.get("excerpt"),

            company=raw_job["companyName"],
            company_slug=raw_job.get("companySlug"),
            company_logo=raw_job.get("companyLogo"),

            employment_type=raw_job.get(
                "employmentType"
            ),

            minimum_salary=raw_job.get(
                "minSalary"
            ),
            maximum_salary=raw_job.get(
                "maxSalary"
            ),
            salary_period=raw_job.get(
                "salaryPeriod"
            ),
            currency=raw_job.get(
                "currency"
            ),

            seniority=raw_job.get(
                "seniority",
                [],
            ),

            location_restrictions=raw_job.get(
                "locationRestrictions",
                [],
            ),

            timezone_restrictions=raw_job.get(
                "timezoneRestrictions",
                [],
            ),

            categories=raw_job.get(
                "categories",
                [],
            ),

            parent_categories=raw_job.get(
                "parentCategories",
                [],
            ),

            description=raw_job.get(
                "description",
                "",
            ),

            published_at=published_at,
            expires_at=expires_at,

            application_url=raw_job[
                "applicationLink"
            ],

            source_url=raw_job[
                "guid"
            ],

            content_hash=content_hash,

            fetched_at=now,
        )

    @staticmethod
    def _timestamp_to_datetime(
        timestamp: int | None,
    ) -> datetime | None:

        if timestamp is None:
            return None

        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        )

    @staticmethod
    def _create_content_hash(
        raw_job: dict,
    ) -> str:

        content = "|".join(
            [
                str(
                    raw_job.get(
                        "title",
                        "",
                    )
                ),
                str(
                    raw_job.get(
                        "companyName",
                        "",
                    )
                ),
                str(
                    raw_job.get(
                        "description",
                        "",
                    )
                ),
                str(
                    raw_job.get(
                        "applicationLink",
                        "",
                    )
                ),
            ]
        )

        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()