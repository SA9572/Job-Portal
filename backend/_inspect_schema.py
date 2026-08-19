from app.database.config import engine
from sqlalchemy import inspect

insp = inspect(engine)
cols = insp.get_columns("jobs")
for c in cols:
    print(f"  {c['name']:30s} {str(c['type']):20s} nullable={c['nullable']}")
