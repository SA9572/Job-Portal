from app.services.ingestion_service import IngestionService


service = IngestionService()

print("========== INGESTION SERVICE TEST ==========")

result = service.run(
    max_pages=3,
    page_size=20,
)

print()
print("========== INGESTION RESULT ==========")

print("Source:", result.source)

print("Pages attempted:", result.pages_attempted)
print("Pages succeeded:", result.pages_succeeded)
print("Pages failed:", result.pages_failed)

print("Jobs fetched:", result.jobs_fetched)
print("Jobs valid:", result.jobs_valid)
print("Jobs invalid:", result.jobs_invalid)

print("Jobs new:", result.jobs_new)
print("Jobs duplicate:", result.jobs_duplicate)
print("Jobs changed:", result.jobs_changed)

print("Errors:", len(result.errors))