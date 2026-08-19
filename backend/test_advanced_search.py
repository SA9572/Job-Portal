from app.database.config import SessionLocal
from app.database.job_repository import JobRepository


print("========== ADVANCED SEARCH TEST ==========")

session = SessionLocal()

try:

    repository = JobRepository(session)

    # =========================================
    # TEST 1: BASIC SEARCH
    # =========================================

    print()
    print("========== TEST 1: SEARCH ==========")

    jobs, total = repository.get_jobs(
        search="machine learning",
        limit=5,
        offset=0,
    )

    print("Total matching:", total)
    print("Returned:", len(jobs))

    for job in jobs:
        print(
            f"- {job.title} | {job.company}"
        )

    # =========================================
    # TEST 2: LOCATION
    # =========================================

    print()
    print("========== TEST 2: LOCATION ==========")

    jobs, total = repository.get_jobs(
        location="India",
        limit=5,
        offset=0,
    )

    print("Total matching:", total)
    print("Returned:", len(jobs))

    for job in jobs:
        print(
            f"- {job.title} | "
            f"{job.location_restrictions}"
        )

    # =========================================
    # TEST 3: SENIORITY
    # =========================================

    print()
    print("========== TEST 3: SENIORITY ==========")

    jobs, total = repository.get_jobs(
        seniority="Senior",
        limit=5,
        offset=0,
    )

    print("Total matching:", total)
    print("Returned:", len(jobs))

    for job in jobs:
        print(
            f"- {job.title} | "
            f"{job.seniority}"
        )

    # =========================================
    # TEST 4: CATEGORY
    # =========================================

    print()
    print("========== TEST 4: CATEGORY ==========")

    jobs, total = repository.get_jobs(
        category="Data Science",
        limit=5,
        offset=0,
    )

    print("Total matching:", total)
    print("Returned:", len(jobs))

    for job in jobs:
        print(
            f"- {job.title} | "
            f"{job.categories}"
        )

    # =========================================
    # TEST 5: MULTIPLE FILTERS
    # =========================================

    print()
    print(
        "========== TEST 5: MULTIPLE FILTERS =========="
    )

    jobs, total = repository.get_jobs(
        search="machine learning",
        location="India",
        seniority="Senior",
        minimum_salary=50000,
        limit=10,
        offset=0,
    )

    print("Total matching:", total)
    print("Returned:", len(jobs))

    for job in jobs:
        print(
            f"- {job.title} | "
            f"{job.company} | "
            f"{job.location_restrictions} | "
            f"{job.seniority}"
        )

    # =========================================
    # TEST 6: SALARY SORTING
    # =========================================

    print()
    print(
        "========== TEST 6: SALARY HIGH =========="
    )

    jobs, total = repository.get_jobs(
        sort_by="salary_high",
        limit=5,
        offset=0,
    )

    print("Total matching:", total)
    print("Returned:", len(jobs))

    for job in jobs:
        print(
            f"- {job.title} | "
            f"Max salary: {job.maximum_salary}"
        )

    # =========================================
    # TEST 7: PAGINATION
    # =========================================

    print()
    print(
        "========== TEST 7: PAGINATION =========="
    )

    jobs_page_1, total = repository.get_jobs(
        limit=5,
        offset=0,
    )

    jobs_page_2, _ = repository.get_jobs(
        limit=5,
        offset=5,
    )

    print("Total:", total)
    print(
        "Page 1:",
        len(jobs_page_1)
    )
    print(
        "Page 2:",
        len(jobs_page_2)
    )

    if jobs_page_1 and jobs_page_2:

        print(
            "First job page 1:",
            jobs_page_1[0].title
        )

        print(
            "First job page 2:",
            jobs_page_2[0].title
        )

    print()
    print("========== TEST COMPLETED ==========")

finally:

    session.close()