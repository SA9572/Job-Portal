from app.sources.himalayas import HimalayasSource
from app.services.deduplicator import JobDeduplicator


source = HimalayasSource()

jobs = source.fetch_jobs(limit=1)

job = jobs[0]

deduplicator = JobDeduplicator()

print("========== DUPLICATE TEST ==========")

result_1 = deduplicator.check(job)

print("First check:", result_1)

result_2 = deduplicator.check(job)

print("Second check:", result_2)


print("\n========== CHANGED CONTENT TEST ==========")

job_copy = job.model_copy(
    update={
        "content_hash": "different-content-hash"
    }
)

result_3 = deduplicator.check(job_copy)

print("Changed job check:", result_3)

print("\n========== EXPECTED ==========")

print("First check: new")
print("Second check: duplicate")
print("Changed job check: changed")