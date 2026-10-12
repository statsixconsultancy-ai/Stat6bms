import sqlite3
import glob

crm_tables = [
    "crm_quote_items",
    "crm_quotes",
    "crm_deals",
    "crm_contacts",
    "crm_leads",
    "crm_companies"
]

for db in glob.glob("backend/data/*.db"):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    existing_tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    deleted = {}
    for tbl in crm_tables:
        if tbl in existing_tables:
            count = cur.execute(f"SELECT count(*) FROM {tbl}").fetchone()[0]
            if count > 0:
                cur.execute(f"DELETE FROM {tbl}")
                deleted[tbl] = count
    conn.commit()
    conn.close()
    if deleted:
        print(f"Purged from {db}: {deleted}")
    else:
        print(f"Clean (0 CRM records) in {db}")
