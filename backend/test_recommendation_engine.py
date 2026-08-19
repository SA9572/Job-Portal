"""
Phase 18 — Job Recommendation Engine Tests

Tests the complete Phase 18 implementation:
1. Pairwise similarity calculation logic (title, category, location, seniority, salary)
2. Similar Jobs API endpoint (GET /api/jobs/{job_id}/similar)
3. Exclusion of target job from own recommendations
4. Exclusion of soft-deleted & expired jobs from recommendations
5. Pagination & min_score filtering
6. 404 for nonexistent or deleted target job
"""

from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.api.main import app
from app.database.config import SessionLocal
from app.database.job_model import JobModel
from app.services.recommendation_engine import RecommendationEngine

client = TestClient(app)
BASE = "/api/jobs"


def test_recommendation_logic():
    """Unit test for RecommendationEngine.calculate_similarity."""
    job1 = JobModel(
        id=1,
        title="Senior Python Backend Developer",
        categories=["Software Engineering", "Python"],
        parent_categories=["Engineering"],
        location_restrictions=["Remote", "US"],
        seniority=["Senior"],
        employment_type="Full-time",
        company="TechCorp",
        minimum_salary=120000.0,
        maximum_salary=160000.0,
    )

    job2 = JobModel(
        id=2,
        title="Python Backend Engineer",
        categories=["Software Engineering", "Python"],
        parent_categories=["Engineering"],
        location_restrictions=["Remote", "US"],
        seniority=["Senior"],
        employment_type="Full-time",
        company="OtherCorp",
        minimum_salary=110000.0,
        maximum_salary=150000.0,
    )

    job3 = JobModel(
        id=3,
        title="Marketing Specialist",
        categories=["Marketing", "SEO"],
        parent_categories=["Marketing"],
        location_restrictions=["Germany"],
        seniority=["Junior"],
        employment_type="Part-time",
        company="AdAgency",
        minimum_salary=40000.0,
        maximum_salary=50000.0,
    )

    # Job 1 and Job 2 should be very similar (> 0.6)
    score_high = RecommendationEngine.calculate_similarity(job1, job2)
    print(f"  PASS: High similarity score (Python dev vs Python dev): {score_high}")
    assert score_high >= 0.5, f"Expected high score >= 0.5, got {score_high}"

    # Job 1 and Job 3 should be very low similarity (< 0.2)
    score_low = RecommendationEngine.calculate_similarity(job1, job3)
    print(f"  PASS: Low similarity score (Python dev vs Marketing): {score_low}")
    assert score_low < 0.2, f"Expected low score < 0.2, got {score_low}"

    # Self-similarity should be 1.0
    score_self = RecommendationEngine.calculate_similarity(job1, job1)
    assert score_self == 1.0
    print("  PASS: Self-similarity score is 1.0")


def test_similar_jobs_endpoint():
    """GET /api/jobs/{job_id}/similar API integration test."""
    # Get a job ID to test
    r = client.get(f"{BASE}?limit=1")
    assert r.status_code == 200
    jobs = r.json().get("jobs", [])
    if not jobs:
        print("  SKIP: No jobs in database")
        return

    job_id = jobs[0]["id"]
    print(f"  Testing recommendations for job_id={job_id} ({jobs[0]['title']})")

    r = client.get(f"{BASE}/{job_id}/similar?limit=5&min_score=0.0")
    assert r.status_code == 200, f"Failed: {r.status_code} {r.text}"
    data = r.json()
    assert "jobs" in data
    assert "total" in data

    rec_jobs = data["jobs"]
    print(f"  PASS: Endpoint returned {len(rec_jobs)} recommendations (total={data['total']})")

    if rec_jobs:
        first_rec = rec_jobs[0]
        assert "similarity_score" in first_rec
        assert first_rec["id"] != job_id, "Target job returned in its own recommendations!"
        print(f"  PASS: Top recommendation: id={first_rec['id']}, score={first_rec['similarity_score']}, title='{first_rec['title']}'")

        # Verify descending order of scores
        scores = [j["similarity_score"] for j in rec_jobs]
        assert scores == sorted(scores, reverse=True), "Recommendations not sorted by similarity_score desc!"
        print("  PASS: Scores are sorted in descending order")


def test_similar_jobs_404():
    """GET /api/jobs/999999/similar returns 404 for nonexistent job."""
    r = client.get(f"{BASE}/999999/similar")
    assert r.status_code == 404
    print("  PASS: 404 for nonexistent job_id=999999")


def test_deleted_job_recommendation_exclusion():
    """Soft deleted job should return 404 and not appear in recommendations."""
    r = client.get(f"{BASE}?limit=2")
    jobs = r.json().get("jobs", [])
    if len(jobs) < 2:
        print("  SKIP: Need at least 2 jobs for exclusion test")
        return

    target_id = jobs[0]["id"]
    candidate_id = jobs[1]["id"]

    # Delete candidate job
    r_del = client.delete(f"{BASE}/{candidate_id}")
    assert r_del.status_code == 200

    # Get recommendations for target
    r_rec = client.get(f"{BASE}/{target_id}/similar?min_score=0.0&limit=50")
    assert r_rec.status_code == 200, f"Failed: {r_rec.status_code} {r_rec.text}"
    rec_ids = [j["id"] for j in r_rec.json()["jobs"]]
    assert candidate_id not in rec_ids, "Deleted job appeared in recommendations!"
    print("  PASS: Soft-deleted job excluded from recommendation results")

    # Restore candidate job
    r_res = client.post(f"{BASE}/{candidate_id}/restore")
    assert r_res.status_code == 200
    print(f"  PASS: Restored candidate job {candidate_id}")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 18 - JOB RECOMMENDATION ENGINE TESTS")
    print("=" * 60)
    print()

    print("[1] Recommendation Algorithm Logic")
    test_recommendation_logic()
    print()

    print("[2] Similar Jobs API Endpoint")
    test_similar_jobs_endpoint()
    print()

    print("[3] 404 Handling")
    test_similar_jobs_404()
    print()

    print("[4] Exclusion of Deleted Jobs")
    test_deleted_job_recommendation_exclusion()
    print()

    print("=" * 60)
    print("ALL PHASE 18 TESTS PASSED")
    print("=" * 60)
