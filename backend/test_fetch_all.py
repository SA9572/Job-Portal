from app.sources.himalayas import HimalayasSource


source = HimalayasSource()

print("========== MULTI-PAGE INGESTION ==========")

jobs = source.fetch_all_jobs(
    max_pages=3,
    page_size=20,
)

print("Total jobs fetched:", len(jobs))

print("\n========== FIRST 5 JOBS ==========")

for job in jobs[:5]:
    print("-", job.title)

print("\n========== LAST 5 JOBS ==========")

for job in jobs[-5:]:
    print("-", job.title)