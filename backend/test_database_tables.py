from sqlalchemy import inspect

from app.database.config import engine


print(
    "========== DATABASE TABLE TEST =========="
)

inspector = inspect(engine)

tables = inspector.get_table_names()

print("Tables found:")

for table in tables:
    print("-", table)

print()

required_tables = {
    "jobs",
    "ingestion_runs",
}

missing_tables = (
    required_tables - set(tables)
)

if not missing_tables:

    print(
        "Required tables: SUCCESS"
    )

else:

    print(
        "Missing tables:",
        sorted(missing_tables),
    )