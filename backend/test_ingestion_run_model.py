from app.database.ingestion_run_model import (
    IngestionRunModel,
)


print(
    "========== INGESTION RUN MODEL TEST =========="
)

print(
    "Table name:",
    IngestionRunModel.__tablename__,
)

print()
print("========== COLUMNS ==========")

for column in IngestionRunModel.__table__.columns:

    print(
        f"- {column.name}: "
        f"{column.type}"
    )

print()
print(
    "IngestionRunModel: SUCCESS"
)