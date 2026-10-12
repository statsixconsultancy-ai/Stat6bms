import sqlite3
import os

print("=== Starting Cleanup of Scheduled Tasks and Duplicate Mock Records ===")

# 1. CLEANUP AUTOMATION.DB
db_auto = "backend/data/automation.db"
if os.path.exists(db_auto):
    conn = sqlite3.connect(db_auto)
    cur = conn.cursor()
    # Purge all scheduled tasks and approvals
    cur.execute("DELETE FROM auto_scheduled_tasks")
    cur.execute("DELETE FROM auto_hitl_approvals")
    cur.execute("DELETE FROM auto_logs")
    print(f"Purged all scheduled tasks and approvals from {db_auto}")
    
    # Drop orphan tables from earlier fallback
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    allowed_auto_tables = {"auto_scheduled_tasks", "auto_hitl_approvals", "auto_rules", "auto_logs", "sqlite_sequence"}
    for t in tables:
        if t not in allowed_auto_tables and not t.startswith("sqlite_"):
            cur.execute(f"DROP TABLE {t}")
            print(f"  Dropped orphan table {t} from {db_auto}")
    conn.commit()
    conn.close()

# 2. CLEANUP SUPPORT.DB
db_sup = "backend/data/support.db"
if os.path.exists(db_sup):
    conn = sqlite3.connect(db_sup)
    cur = conn.cursor()
    cur.execute("DELETE FROM sup_ticket_messages")
    cur.execute("DELETE FROM sup_tickets")
    conn.commit()
    conn.close()
    print(f"Cleaned support tickets and messages from {db_sup} (0 records, clean queue)")

# 3. CLEANUP FINANCE.DB (Deduplicate invoices)
db_fin = "backend/data/finance.db"
if os.path.exists(db_fin):
    conn = sqlite3.connect(db_fin)
    cur = conn.cursor()
    # Keep unique invoices INV-2026-001, INV-2026-002, INV-2026-003, INV-2024-002
    cur.execute("DELETE FROM fin_invoices WHERE invoice_number NOT IN ('INV-2026-001', 'INV-2026-002', 'INV-2026-003', 'INV-2024-002')")
    cur.execute("DELETE FROM fin_invoice_items WHERE invoice_id NOT IN (SELECT id FROM fin_invoices)")
    cur.execute("DELETE FROM fin_payments WHERE invoice_id NOT IN (SELECT id FROM fin_invoices)")
    conn.commit()
    remaining_inv = cur.execute("SELECT invoice_number, client_name, total_amount, status FROM fin_invoices").fetchall()
    print(f"Cleaned duplicate invoices from {db_fin}. Remaining clean invoices: {remaining_inv}")
    conn.close()

# 4. CLEANUP PROCUREMENT.DB (Deduplicate POs)
db_proc = "backend/data/procurement.db"
if os.path.exists(db_proc):
    conn = sqlite3.connect(db_proc)
    cur = conn.cursor()
    # Deduplicate purchase orders
    cur.execute("DELETE FROM proc_po_line_items WHERE po_id IN (SELECT id FROM proc_purchase_orders WHERE po_number > 'PO-2026-002')")
    cur.execute("DELETE FROM proc_purchase_orders WHERE po_number > 'PO-2026-002'")
    conn.commit()
    conn.close()
    print(f"Deduplicated purchase orders in {db_proc}")

# 5. CLEANUP MARKETING.DB (Deduplicate campaigns)
db_mkt = "backend/data/marketing.db"
if os.path.exists(db_mkt):
    conn = sqlite3.connect(db_mkt)
    cur = conn.cursor()
    # Keep only primary unique campaigns
    cur.execute("DELETE FROM marketing_campaigns WHERE id NOT IN (SELECT MIN(id) FROM marketing_campaigns GROUP BY name)")
    conn.commit()
    conn.close()
    print(f"Deduplicated marketing campaigns in {db_mkt}")

# 6. CLEANUP PROJECTS.DB (Deduplicate projects/sprints)
db_prj = "backend/data/projects.db"
if os.path.exists(db_prj):
    conn = sqlite3.connect(db_prj)
    cur = conn.cursor()
    cur.execute("DELETE FROM prj_projects WHERE id NOT IN (SELECT MIN(id) FROM prj_projects GROUP BY code)")
    cur.execute("DELETE FROM prj_sprints WHERE id NOT IN (SELECT MIN(id) FROM prj_sprints GROUP BY name)")
    conn.commit()
    conn.close()
    print(f"Deduplicated projects and sprints in {db_prj}")

print("=== Cleanup Complete ===")
