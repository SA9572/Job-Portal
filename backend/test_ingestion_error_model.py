from app.database.ingestion_error_model import (
    IngestionErrorModel,
)


print(
    "========== INGESTION ERROR MODEL TEST =========="
)

print(
    "Table name:",
    IngestionErrorModel.__tablename__,
)

print()
print("========== COLUMNS ==========")

for column in IngestionErrorModel.__table__.columns:

    print(
        f"- {column.name}: "
        f"{column.type}"
    )

print()
print("========== FOREIGN KEYS ==========")

for column in IngestionErrorModel.__table__.columns:

    for foreign_key in column.foreign_keys:

        print(
            f"- {column.name} -> "
            f"{foreign_key.target_fullname}"
        )

print()
print(
    "IngestionErrorModel: SUCCESS"
)