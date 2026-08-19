from app.database.base import Base
from app.database.config import engine, SessionLocal
from app.database.job_model import JobModel
from app.database.ingestion_run_model import IngestionRunModel
from app.database.ingestion_error_model import IngestionErrorModel
from app.database.job_change_model import JobChangeModel
from app.database.user_model import UserModel
from app.database.saved_job_model import SavedJobModel
from app.database.job_alert_model import JobAlertModel
from app.database.user_repository import UserRepository

from sqlalchemy import text


def init_database():

    Base.metadata.create_all(
        bind=engine
    )

    # -----------------------------------------
    # EXISTING INDEXES (columns already exist)
    # -----------------------------------------

    existing_indexes = [
        "CREATE INDEX IF NOT EXISTS ix_jobs_published_at ON jobs (published_at);",
        "CREATE INDEX IF NOT EXISTS ix_jobs_company ON jobs (company);",
        "CREATE INDEX IF NOT EXISTS ix_jobs_employment_type ON jobs (employment_type);",
        "CREATE INDEX IF NOT EXISTS ix_jobs_minimum_salary ON jobs (minimum_salary);",
        "CREATE INDEX IF NOT EXISTS ix_jobs_maximum_salary ON jobs (maximum_salary);",
        "CREATE INDEX IF NOT EXISTS ix_jobs_created_at ON jobs (created_at);",
        "CREATE INDEX IF NOT EXISTS ix_jobs_source ON jobs (source);",
        "CREATE INDEX IF NOT EXISTS ix_jobs_expires_at ON jobs (expires_at);",
    ]

    # -----------------------------------------
    # SAFE COLUMN MIGRATION
    # -----------------------------------------

    safe_alter_statements = [
        "ALTER TABLE jobs ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT 0;",
        "ALTER TABLE jobs ADD COLUMN deleted_at DATETIME;",
        "ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';",
        "ALTER TABLE saved_jobs ADD COLUMN notes TEXT;",
        "ALTER TABLE job_alerts ADD COLUMN keywords VARCHAR(255);",
        "ALTER TABLE job_alerts ADD COLUMN location VARCHAR(255);",
        "ALTER TABLE job_alerts ADD COLUMN category VARCHAR(255);",
        "ALTER TABLE job_alerts ADD COLUMN seniority VARCHAR(255);",
        "ALTER TABLE job_alerts ADD COLUMN min_salary FLOAT;",
        "ALTER TABLE job_alerts ADD COLUMN frequency VARCHAR(50) DEFAULT 'daily';",
        "ALTER TABLE job_alerts ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1;",
        "ALTER TABLE job_alerts ADD COLUMN last_sent_at DATETIME;",
    ]

    # -----------------------------------------
    # NEW INDEXES
    # -----------------------------------------

    new_indexes = [
        "CREATE INDEX IF NOT EXISTS ix_jobs_is_deleted ON jobs (is_deleted);",
        "CREATE INDEX IF NOT EXISTS ix_users_role ON users (role);",
    ]

    with engine.connect() as conn:

        for stmt in existing_indexes:
            conn.execute(text(stmt))

        for stmt in safe_alter_statements:
            try:
                conn.execute(text(stmt))
            except Exception:
                pass

        for stmt in new_indexes:
            try:
                conn.execute(text(stmt))
            except Exception:
                pass

        # -----------------------------------------
        # FTS5 FULL-TEXT SEARCH VIRTUAL TABLE & TRIGGERS
        # -----------------------------------------
        conn.execute(text(
            "CREATE VIRTUAL TABLE IF NOT EXISTS jobs_fts USING fts5("
            "job_id UNINDEXED, title, company, excerpt, description, tokenize='unicode61'"
            ");"
        ))

        # Triggers to keep FTS table in sync
        triggers = [
            """
            CREATE TRIGGER IF NOT EXISTS jobs_ai AFTER INSERT ON jobs BEGIN
                INSERT INTO jobs_fts(rowid, job_id, title, company, excerpt, description)
                VALUES (new.id, new.id, new.title, new.company, COALESCE(new.excerpt, ''), new.description);
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS jobs_ad AFTER DELETE ON jobs BEGIN
                DELETE FROM jobs_fts WHERE rowid = old.id;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS jobs_au AFTER UPDATE ON jobs BEGIN
                UPDATE jobs_fts SET
                    title = new.title,
                    company = new.company,
                    excerpt = COALESCE(new.excerpt, ''),
                    description = new.description
                WHERE rowid = old.id;
            END;
            """
        ]

        for trig in triggers:
            try:
                conn.execute(text(trig))
            except Exception:
                pass

        # Populate jobs_fts with existing jobs if empty
        fts_count = conn.execute(text("SELECT COUNT(*) FROM jobs_fts")).scalar()
        if fts_count == 0:
            conn.execute(text(
                "INSERT INTO jobs_fts(rowid, job_id, title, company, excerpt, description) "
                "SELECT id, id, title, company, COALESCE(excerpt, ''), description FROM jobs;"
            ))

        conn.commit()

    # -----------------------------------------
    # SEED DEFAULT ADMIN USER IF NOT EXISTS
    # -----------------------------------------
    session = SessionLocal()
    try:
        repo = UserRepository(session)
        admin = repo.get_by_email("admin@jobrequired.com")
        if not admin:
            repo.create(
                email="admin@jobrequired.com",
                password="AdminPass123!",
                full_name="System Administrator",
                role="admin",
            )
            print("Default admin user created: admin@jobrequired.com")
    finally:
        session.close()


if __name__ == "__main__":

    init_database()

    print(
        "Database tables, user schemas, and performance indexes verified successfully"
    )