from app.database.config import engine
from sqlalchemy import text

with engine.connect() as conn:
    rows = conn.execute(text("SELECT rowid, bm25(jobs_fts), snippet(jobs_fts, -1, '<b>', '</b>', '...', 15) FROM jobs_fts WHERE jobs_fts MATCH 'python*' LIMIT 3")).all()
    for r in rows:
        print(r)
