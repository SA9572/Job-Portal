from app.database.job_change_model import (
    JobChangeModel,
)


print(
    "========== JOB CHANGE MODEL TEST =========="
)

print(
    "Table name:",
    JobChangeModel.__tablename__,
)

print()
print("========== COLUMNS ==========")

for column in JobChangeModel.__table__.columns:

    print(
        f"- {column.name}: "
        f"{column.type}"
    )

print()
print("========== FOREIGN KEYS ==========")

for column in JobChangeModel.__table__.columns:

    for foreign_key in column.foreign_keys:

        print(
            f"- {column.name} -> "
            f"{foreign_key.target_fullname}"
        )

print()
print(
    "JobChangeModel: SUCCESS"
)