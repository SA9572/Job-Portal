from app.sources.himalayas import HimalayasSource
from app.services.validator import JobValidator


source = HimalayasSource()

jobs = source.fetch_jobs(limit=1)

job = jobs[0]

validator = JobValidator()

errors = validator.validate(job)

print("========== VALIDATION RESULT ==========")

if errors:
    print("VALID: NO")

    for error in errors:
        print("ERROR:", error)

else:
    print("VALID: YES")