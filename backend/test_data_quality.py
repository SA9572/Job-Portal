from datetime import datetime, timezone

from app.models.job import Job
from app.services.sanitizer import DataSanitizer


print("========== DATA QUALITY & SANITIZATION TEST ==========")

# =========================================
# TEST 1: TEXT CLEANING & HTML UNESCAPING
# =========================================

print()
print("========== TEST 1: TEXT CLEANING & HTML UNESCAPING ==========")

raw_title = "  Senior &amp; Lead  Developer  "
clean_title = DataSanitizer.clean_text(raw_title)

print("Raw title:", repr(raw_title))
print("Clean title:", repr(clean_title))

assert clean_title == "Senior & Lead Developer"

# =========================================
# TEST 2: HTML TAG STRIPPING
# =========================================

print()
print("========== TEST 2: HTML TAG STRIPPING ==========")

html_excerpt = "<h3>Job Summary</h3><p>We are hiring a <strong>Full Stack Developer</strong>.</p>"
clean_excerpt = DataSanitizer.strip_html_tags(html_excerpt)

print("HTML excerpt:", repr(html_excerpt))
print("Clean excerpt:", repr(clean_excerpt))

assert clean_excerpt == "Job Summary We are hiring a Full Stack Developer ."

# =========================================
# TEST 3: URL SANITIZATION
# =========================================

print()
print("========== TEST 3: URL SANITIZATION ==========")

valid_url = DataSanitizer.clean_url("  https://himalayas.app/jobs/123  ")
invalid_url = DataSanitizer.clean_url("javascript:alert(1)")

print("Valid URL:", repr(valid_url))
print("Invalid URL:", repr(invalid_url))

assert valid_url == "https://himalayas.app/jobs/123"
assert invalid_url is None

# =========================================
# TEST 4: SALARY NORMALIZATION
# =========================================

print()
print("========== TEST 4: SALARY NORMALIZATION ==========")

now = datetime.now(timezone.utc)

dirty_job = Job(
    source="himalayas",
    external_id="dirty-123",
    title="<h1>  Lead Architect &amp; Dev </h1>",
    excerpt="<p>Summary with <b>tags</b></p>",
    company=" Tech  Corp &amp; Co ",
    company_slug=None,
    company_logo="invalid-url-schema",
    employment_type=" Full Time ",
    minimum_salary=200000.0,
    maximum_salary=120000.0,  # Min > Max inversion
    salary_period="year",
    currency="USD",
    seniority=["Senior", "", "  ", "Architect"],
    location_restrictions=[" India ", ""],
    timezone_restrictions=[],
    categories=["Python", "  "],
    parent_categories=[],
    description="<script>alert(1)</script>Clean description with formatting.",
    published_at=now,
    expires_at=None,
    application_url="  https://example.com/apply  ",
    source_url="  https://example.com/source  ",
    content_hash="hash123",
    fetched_at=now,
)

sanitized = DataSanitizer.sanitize(dirty_job)

print("Sanitized Title:", repr(sanitized.title))
print("Sanitized Company:", repr(sanitized.company))
print("Sanitized Min Salary:", sanitized.minimum_salary)
print("Sanitized Max Salary:", sanitized.maximum_salary)
print("Sanitized Seniority List:", sanitized.seniority)
print("Sanitized Locations:", sanitized.location_restrictions)
print("Sanitized Categories:", sanitized.categories)
print("Sanitized Logo URL:", sanitized.company_logo)

assert sanitized.title == "Lead Architect & Dev"
assert sanitized.company == "Tech Corp & Co"
assert sanitized.minimum_salary == 120000.0
assert sanitized.maximum_salary == 200000.0
assert sanitized.seniority == ["Senior", "Architect"]
assert sanitized.location_restrictions == ["India"]
assert sanitized.categories == ["Python"]
assert sanitized.company_logo is None
assert str(sanitized.application_url) == "https://example.com/apply"

print()
print("========== DATA QUALITY & SANITIZATION TEST COMPLETED ==========")
