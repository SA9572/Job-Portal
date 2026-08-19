import os

from app.core.config import settings


print("========== CENTRALIZED CONFIGURATION TEST ==========")

# =========================================
# TEST 1: SETTINGS OBJECT VALUES
# =========================================

print()
print("========== TEST 1: SETTINGS OBJECT VALUES ==========")

print("Project Name:", settings.PROJECT_NAME)
print("Version:", settings.VERSION)
print("Database URL:", settings.DATABASE_URL)
print("Log Level:", settings.LOG_LEVEL)
print("CORS Origins:", settings.CORS_ORIGINS)
print("Ingestion Interval:", settings.INGESTION_INTERVAL_MINUTES)
print("Secret Key configured:", bool(settings.SECRET_KEY))

assert settings.PROJECT_NAME == "JOB REQUIRED"
assert settings.VERSION == "1.0.0"
assert "sqlite" in settings.DATABASE_URL
assert isinstance(settings.CORS_ORIGINS, list)
assert len(settings.CORS_ORIGINS) > 0

# =========================================
# TEST 2: VERIFY PROJECT CONFIG FILES
# =========================================

print()
print("========== TEST 2: VERIFY CONFIG FILES ==========")

base_dir = os.path.dirname(os.path.abspath(__file__))

env_file = os.path.join(base_dir, ".env")
env_example_file = os.path.join(base_dir, ".env.example")
gitignore_file = os.path.join(base_dir, ".gitignore")

print(".env exists:", os.path.exists(env_file))
print(".env.example exists:", os.path.exists(env_example_file))
print(".gitignore exists:", os.path.exists(gitignore_file))

assert os.path.exists(env_file)
assert os.path.exists(env_example_file)
assert os.path.exists(gitignore_file)

with open(gitignore_file, "r", encoding="utf-8") as f:
    gitignore_content = f.read()

assert ".env" in gitignore_content
assert "*.db" in gitignore_content
assert "logs/" in gitignore_content
assert ".venv/" in gitignore_content

print("Gitignore rules verified successfully.")

print()
print("========== CENTRALIZED CONFIGURATION TEST COMPLETED ==========")
