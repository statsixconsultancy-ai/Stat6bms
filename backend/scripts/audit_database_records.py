import sqlite3
import glob

for db in sorted(glob.glob("backend/data/*.db")):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
    non_empty = {}
    for t in tables:
        try:
            cnt = cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
            if cnt > 0:
                non_empty[t] = cnt
        except Exception:
            pass
    conn.close()
    if non_empty:
        print(f"=== {db} ===")
        for t, c in non_empty.items():
            print(f"  {t}: {c}")
