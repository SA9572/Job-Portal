from app.database.config import SessionLocal
from app.database.job_repository import JobRepository


print("========== SORTING TEST ==========")

session = SessionLocal()

try:

    repository = JobRepository(session)

    # =========================================
    # TEST 1: LEGACY sort_by = salary_high
    # =========================================

    print()
    print(
        "========== TEST 1: LEGACY salary_high =========="
    )

    jobs, total = repository.get_jobs(
        sort_by="salary_high",
        limit=3,
    )

    print("Total:", total)
    print("Returned:", len(jobs))

    for job in jobs:
        print(
            f"- {job.title} | "
            f"Max: {job.maximum_salary}"
        )

    # =========================================
    # TEST 2: LEGACY sort_by = newest
    # =========================================

    print()
    print(
        "========== TEST 2: LEGACY newest =========="
    )

    jobs, total = repository.get_jobs(
        sort_by="newest",
        limit=3,
    )

    print("Total:", total)

    for job in jobs:
        print(
            f"- {job.title} | "
            f"Published: {job.published_at}"
        )

    # =========================================
    # TEST 3: sort_by = published_at
    #         sort_order = desc
    # =========================================

    print()
    print(
        "========== TEST 3: published_at DESC =========="
    )

    jobs, total = repository.get_jobs(
        sort_by="published_at",
        sort_order="desc",
        limit=3,
    )

    print("Total:", total)

    for job in jobs:
        print(
            f"- {job.title} | "
            f"Published: {job.published_at}"
        )

    # =========================================
    # TEST 4: sort_by = title
    #         sort_order = asc
    # =========================================

    print()
    print(
        "========== TEST 4: title ASC =========="
    )

    jobs, total = repository.get_jobs(
        sort_by="title",
        sort_order="asc",
        limit=5,
    )

    print("Total:", total)

    for job in jobs:
        print(
            f"- {job.title}"
        )

    # =========================================
    # TEST 5: sort_by = company
    #         sort_order = asc
    # =========================================

    print()
    print(
        "========== TEST 5: company ASC =========="
    )

    jobs, total = repository.get_jobs(
        sort_by="company",
        sort_order="asc",
        limit=5,
    )

    print("Total:", total)

    for job in jobs:
        print(
            f"- {job.company} | "
            f"{job.title}"
        )

    # =========================================
    # TEST 6: sort_by = maximum_salary
    #         sort_order = desc
    # =========================================

    print()
    print(
        "========== TEST 6: maximum_salary DESC =========="
    )

    jobs, total = repository.get_jobs(
        sort_by="maximum_salary",
        sort_order="desc",
        limit=3,
    )

    print("Total:", total)

    for job in jobs:
        print(
            f"- {job.title} | "
            f"Max: {job.maximum_salary}"
        )

    # =========================================
    # TEST 7: INVALID sort_by
    # =========================================

    print()
    print(
        "========== TEST 7: INVALID sort_by =========="
    )

    try:

        repository.get_jobs(
            sort_by="nonexistent_field",
            limit=3,
        )

        print("ERROR: should have raised ValueError")

    except ValueError as exc:

        print("Caught ValueError:", exc)

    # =========================================
    # TEST 8: INVALID sort_order
    # =========================================

    print()
    print(
        "========== TEST 8: INVALID sort_order =========="
    )

    try:

        repository.get_jobs(
            sort_by="title",
            sort_order="random",
            limit=3,
        )

        print("ERROR: should have raised ValueError")

    except ValueError as exc:

        print("Caught ValueError:", exc)

    # =========================================
    # TEST 9: DEFAULT SORT (no sort params)
    # =========================================

    print()
    print(
        "========== TEST 9: DEFAULT SORT =========="
    )

    jobs, total = repository.get_jobs(
        limit=3,
    )

    print("Total:", total)

    for job in jobs:
        print(
            f"- ID: {job.id} | "
            f"{job.title}"
        )

    # =========================================
    # TEST 10: SORT + FILTER COMBINED
    # =========================================

    print()
    print(
        "========== TEST 10: SORT + FILTER =========="
    )

    jobs, total = repository.get_jobs(
        seniority="Senior",
        sort_by="maximum_salary",
        sort_order="desc",
        limit=5,
    )

    print("Total:", total)

    for job in jobs:
        print(
            f"- {job.title} | "
            f"Max: {job.maximum_salary} | "
            f"{job.seniority}"
        )

    print()
    print("========== SORTING TEST COMPLETED ==========")

finally:

    session.close()
