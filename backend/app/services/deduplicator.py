from app.models.job import Job


class JobDeduplicator:

    def __init__(self):
        self.seen_jobs: dict[tuple[str, str], str] = {}

    def check(self, job: Job) -> str:
        key = (job.source, job.external_id)

        if key not in self.seen_jobs:
            self.seen_jobs[key] = job.content_hash or ""
            return "new"

        previous_hash = self.seen_jobs[key]

        if previous_hash != (job.content_hash or ""):
            self.seen_jobs[key] = job.content_hash or ""
            return "changed"

        return "duplicate"