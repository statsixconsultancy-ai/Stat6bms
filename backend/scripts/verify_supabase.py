import os
import sys
import psycopg2

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"))

db_url = os.getenv("SUPABASE_DB_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
tables = [r[0] for r in cur.fetchall()]

print("=" * 65)
print(f"  SUPABASE LIVE DATABASE AUDIT ({len(tables)} TABLES)")
print("=" * 65)
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t}";')
    cnt = cur.fetchone()[0]
    print(f"  {t:<35}: {cnt} rows")

conn.close()
