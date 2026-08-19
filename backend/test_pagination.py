from app.sources.himalayas import HimalayasSource


source = HimalayasSource()

print("========== PAGE 1 ==========")

page_1 = source.fetch_jobs(
    limit=20,
    offset=0,
)

print("Page 1 jobs:", len(page_1))

for job in page_1[:3]:
    print("-", job.title)


print("\n========== PAGE 2 ==========")

page_2 = source.fetch_jobs(
    limit=20,
    offset=20,
)

print("Page 2 jobs:", len(page_2))

for job in page_2[:3]:
    print("-", job.title)


print("\n========== PAGE 3 ==========")

page_3 = source.fetch_jobs(
    limit=20,
    offset=40,
)

print("Page 3 jobs:", len(page_3))

for job in page_3[:3]:
    print("-", job.title)