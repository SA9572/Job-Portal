from app.sources.himalayas import HimalayasSource


source = HimalayasSource()

jobs = source.fetch_jobs(limit=1)

print("Number of normalized jobs:", len(jobs))

job = jobs[0]

print("\n========== NORMALIZED JOB ==========\n")

print("Source:", job.source)
print("External ID:", job.external_id)
print("Title:", job.title)
print("Company:", job.company)
print("Employment Type:", job.employment_type)
print("Salary:", job.minimum_salary, "-", job.maximum_salary)
print("Currency:", job.currency)
print("Seniority:", job.seniority)
print("Locations:", job.location_restrictions)
print("Published:", job.published_at)
print("Expires:", job.expires_at)
print("Application URL:", job.application_url)
print("Content Hash:", job.content_hash)
print("Fetched At:", job.fetched_at)