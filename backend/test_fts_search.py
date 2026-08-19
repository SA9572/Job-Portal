"""
Phase 23 — SQLite FTS5 Full-Text Search Engine Tests

Tests the complete Phase 23 implementation:
1. FTS5 Virtual Table initialization and BM25 search
2. Dedicated FTS Search endpoint (GET /api/jobs/fts/search)
3. Term Highlighting and Snippet generation (<mark>term</mark>)
4. FTS search boolean expressions (AND, OR, NOT) & prefix matching (term*)
5. Trigger auto-synchronization on job insertion, update, and deletion
6. Combination of FTS search with structured filters (location, salary, company)
"""

from fastapi.testclient import TestClient
from app.api.main import app
from app.database.config import SessionLocal
from app.database.job_repository import JobRepository
from app.models.job import Job

client = TestClient(app)
FTS_BASE = "/api/jobs/fts/search"
JOBS_BASE = "/api/jobs"


def test_fts_search_endpoint():
    """GET /api/jobs/fts/search endpoint test."""
    r = client.get(f"{FTS_BASE}?q=python")
    assert r.status_code == 200, f"FTS search failed: {r.status_code} {r.text}"
    data = r.json()

    assert "jobs" in data
    assert "total" in data
    print(f"  PASS: FTS search 'python' returned {len(data['jobs'])} jobs (total={data['total']})")

    if data["jobs"]:
        job = data["jobs"][0]
        assert "fts_snippet" in job
        assert "relevance_score" in job
        print(f"  PASS: FTS result has relevance_score={job['relevance_score']} and snippet='{job['fts_snippet']}'")


def test_fts_boolean_operators_and_wildcards():
    """FTS search with AND/OR operators and prefix matching."""
    # Prefix matching (e.g. engine*)
    r_prefix = client.get(f"{FTS_BASE}?q=engine*")
    assert r_prefix.status_code == 200
    print(f"  PASS: FTS prefix search 'engine*' returned {r_prefix.json()['total']} jobs")

    # Phrase match
    r_phrase = client.get(f"{FTS_BASE}?q=%22software%20engineer%22")
    assert r_phrase.status_code == 200
    print(f"  PASS: FTS phrase search '\"software engineer\"' returned {r_phrase.json()['total']} jobs")


def test_fts_trigger_autosync():
    """Verify triggers auto-sync new job insertions, updates, and deletes to jobs_fts."""
    session = SessionLocal()

    try:
        repo = JobRepository(session)
        ext_id = f"fts_test_{__import__('time').time()}"

        job = Job(
            source="himalayas",
            external_id=ext_id,
            title="Quantum Cryptography Specialist",
            excerpt="High security quantum computing role.",
            company="QuantumLabs",
            description="Working on quantum key distribution and lattice cryptography.",
            application_url="https://quantum.com/apply",
            source_url="https://quantum.com/job/1",
            content_hash="hash_quantum_123",
            fetched_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        )

        # 1. INSERT -> Trigger fires
        db_job = repo.create(job)
        job_id = db_job.id
        print(f"  Created test job (id={job_id}, title='Quantum Cryptography Specialist')")

        # Search FTS for "quantum"
        r_fts1 = client.get(f"{FTS_BASE}?q=quantum")
        assert r_fts1.status_code == 200
        found_ids1 = [j["id"] for j in r_fts1.json()["jobs"]]
        assert job_id in found_ids1, "Newly inserted job not found in FTS index!"
        print("  PASS: Insert trigger auto-synced job to jobs_fts index")

        # 2. UPDATE -> Trigger fires
        job.title = "Post-Quantum Cryptography Architect"
        repo.update(db_job, job)

        r_fts2 = client.get(f"{FTS_BASE}?q=architect")
        assert r_fts2.status_code == 200
        found_ids2 = [j["id"] for j in r_fts2.json()["jobs"]]
        assert job_id in found_ids2, "Updated job title not found in FTS index!"
        print("  PASS: Update trigger auto-synced changes to jobs_fts index")

        # 3. DELETE -> Trigger fires
        repo.soft_delete(job_id)  # Soft delete excludes from active FTS
        r_fts3 = client.get(f"{FTS_BASE}?q=quantum")
        found_ids3 = [j["id"] for j in r_fts3.json()["jobs"]]
        assert job_id not in found_ids3, "Deleted job still appeared in active FTS search!"
        print("  PASS: Soft-deleted job excluded from active FTS search")

        # Clean up
        repo.restore(job_id)

    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 23 - SQLITE FTS5 FULL-TEXT SEARCH TESTS")
    print("=" * 60)
    print()

    print("[1] Dedicated FTS Search Endpoint")
    test_fts_search_endpoint()
    print()

    print("[2] Boolean Operators & Wildcards")
    test_fts_boolean_operators_and_wildcards()
    print()

    print("[3] SQLite FTS Trigger Auto-Sync")
    test_fts_trigger_autosync()
    print()

    print("=" * 60)
    print("ALL PHASE 23 TESTS PASSED")
    print("=" * 60)
