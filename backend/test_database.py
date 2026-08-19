from sqlalchemy import text

from app.database.config import engine


print("========== DATABASE CONNECTION TEST ==========")

with engine.connect() as connection:

    result = connection.execute(
        text("SELECT 1")
    )

    value = result.scalar()

print("Database connection: SUCCESS")
print("Test query result:", value)