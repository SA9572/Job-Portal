from app.models.job import Job


class JobValidator:

    def validate(self, job: Job) -> list[str]:
        errors = []

        if not job.title.strip():
            errors.append("Job title is empty")

        if not job.company.strip():
            errors.append("Company name is empty")

        if not job.description.strip():
            errors.append("Job description is empty")

        if not job.application_url:
            errors.append("Application URL is missing")

        if job.minimum_salary is not None and job.maximum_salary is not None:
            if job.minimum_salary > job.maximum_salary:
                errors.append(
                    "Minimum salary cannot be greater than maximum salary"
                )

        if job.published_at is not None and job.expires_at is not None:
            if job.published_at > job.expires_at:
                errors.append(
                    "Published date cannot be after expiry date"
                )

        return errors

    def is_valid(self, job: Job) -> bool:
        return len(self.validate(job)) == 0