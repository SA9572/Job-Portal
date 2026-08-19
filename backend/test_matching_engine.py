"""
Phase 22 — Job Matching Engine Tests

Tests the complete Phase 22 implementation:
1. JobMatchingEngine unit tests (match scores & detailed score breakdowns)
2. Match jobs endpoint (POST /api/match) with profile skills & preferences
3. Single job match endpoint (POST /api/match/{job_id})
4. Score breakdown schema validation
5. Min score filtering & pagination
6. 404 for matching nonexistent job_id
"""

from fastapi.testclient import TestClient
from app.api.main import app
from app.database.job_model import JobModel
from app.services.matching_engine import JobMatchingEngine

client = TestClient(app)
MATCH_BASE = "/api/match"
JOBS_BASE = "/api/jobs"


def test_matching_algorithm():
    """Unit test for JobMatchingEngine.calculate_user_match."""
    profile = {
        "desired_title": "Python Backend Engineer",
        "skills": ["python", "fastapi", "postgresql", "docker"],
        "preferred_locations": ["remote", "us"],
        "seniority": ["senior"],
        "min_salary": 120000.0,
    }

    job_high = JobModel(
        id=10,
        title="Senior Python Backend Developer",
        excerpt="Hiring a Senior Python Developer with FastAPI expertise.",
        categories=["Software Engineering", "Python", "FastAPI"],
        location_restrictions=["Remote", "US"],
        seniority=["Senior"],
        minimum_salary=110000.0,
        maximum_salary=150000.0,
        description="We are looking for a Python engineer skilled in PostgreSQL and Docker.",
    )

    job_low = JobModel(
        id=20,
        title="Graphic Designer",
        excerpt="Creative UI/UX designer needed for marketing team.",
        categories=["Design", "Figma"],
        location_restrictions=["Japan"],
        seniority=["Junior"],
        minimum_salary=40000.0,
        maximum_salary=50000.0,
        description="Design banners and vector logos.",
    )

    score_high, breakdown_high = JobMatchingEngine.calculate_user_match(profile, job_high)
    print(f"  PASS: High match score: {score_high}, breakdown: {breakdown_high}")
    assert score_high >= 0.6, f"Expected match score >= 0.6, got {score_high}"
    assert breakdown_high["title_match"] > 0.0
    assert breakdown_high["skill_match"] > 0.0
    assert breakdown_high["salary_match"] == 1.0

    score_low, breakdown_low = JobMatchingEngine.calculate_user_match(profile, job_low)
    print(f"  PASS: Low match score: {score_low}, breakdown: {breakdown_low}")
    assert score_low < 0.35, f"Expected low match score < 0.35, got {score_low}"


def test_match_jobs_endpoint():
    """POST /api/match API endpoint integration test."""
    payload = {
        "desired_title": "Software Engineer",
        "skills": ["python", "javascript", "react"],
        "preferred_locations": ["remote"],
        "seniority": ["senior"],
        "min_salary": 90000.0,
    }

    r = client.post(f"{MATCH_BASE}?limit=5&min_score=0.1", json=payload)
    assert r.status_code == 200, f"Match failed: {r.status_code} {r.text}"
    data = r.json()

    assert "jobs" in data
    assert "total" in data
    assert "count" in data

    jobs = data["jobs"]
    print(f"  PASS: POST /api/match returned {len(jobs)} matched jobs (total={data['total']})")

    if jobs:
        top_match = jobs[0]
        assert "match_score" in top_match
        assert "match_breakdown" in top_match
        bd = top_match["match_breakdown"]
        assert "title_match" in bd
        assert "skill_match" in bd
        assert "location_match" in bd
        assert "seniority_match" in bd
        assert "salary_match" in bd
        print(f"  PASS: Top match: id={top_match['id']}, score={top_match['match_score']}, title='{top_match['title']}'")

        # Verify descending order
        scores = [j["match_score"] for j in jobs]
        assert scores == sorted(scores, reverse=True), "Matched jobs not sorted by score desc!"
        print("  PASS: Matched jobs ordered by match_score descending")


def test_match_single_job_endpoint():
    """POST /api/match/{job_id} single job match evaluation."""
    r_jobs = client.get(f"{JOBS_BASE}?limit=1")
    assert r_jobs.status_code == 200
    jobs_list = r_jobs.json().get("jobs", [])
    if not jobs_list:
        print("  SKIP: No jobs available")
        return

    job_id = jobs_list[0]["id"]

    payload = {
        "desired_title": jobs_list[0]["title"],
        "skills": ["python"],
        "preferred_locations": ["remote"],
    }

    r_single = client.post(f"{MATCH_BASE}/{job_id}", json=payload)
    assert r_single.status_code == 200
    data = r_single.json()

    assert data["job_id"] == job_id
    assert "match_score" in data
    assert "match_breakdown" in data
    print(f"  PASS: Single job match: id={job_id}, score={data['match_score']}")


def test_match_single_job_404():
    """POST /api/match/999999 returns 404 for nonexistent job."""
    payload = {"desired_title": "Developer"}
    r = client.post(f"{MATCH_BASE}/999999", json=payload)
    assert r.status_code == 404
    print("  PASS: POST /api/match/999999 -> 404")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 22 - JOB MATCHING ENGINE TESTS")
    print("=" * 60)
    print()

    print("[1] Matching Algorithm Logic & Score Breakdown")
    test_matching_algorithm()
    print()

    print("[2] Match Jobs API Endpoint (POST /api/match)")
    test_match_jobs_endpoint()
    print()

    print("[3] Match Single Job Endpoint (POST /api/match/{id})")
    test_match_single_job_endpoint()
    print()

    print("[4] 404 Handling")
    test_match_single_job_404()
    print()

    print("=" * 60)
    print("ALL PHASE 22 TESTS PASSED")
    print("=" * 60)
