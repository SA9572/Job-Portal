from app.database.job_model import JobModel


print("========== JOB DATABASE MODEL TEST ==========")

print("Table name:", JobModel.__tablename__)

print()
print("========== COLUMNS ==========")

for column in JobModel.__table__.columns:
    print(
        f"- {column.name}: "
        f"{column.type}"
    )

print()
print("========== CONSTRAINTS ==========")

for constraint in JobModel.__table__.constraints:
    print(
        f"- {constraint.name}: "
        f"{type(constraint).__name__}"
    )

print()
print("Job database model: SUCCESS")