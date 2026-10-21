import os
import sys
import glob

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

data_dir = os.path.join(backend_dir, "data")
print(f"Cleaning database files in {data_dir}...")
for db_file in glob.glob(os.path.join(data_dir, "*.db")):
    try:
        os.remove(db_file)
        print(f"  Removed {os.path.basename(db_file)}")
    except Exception as e:
        print(f"  Failed to remove {db_file}: {e}")

print("\nInitializing fresh pristine databases with ZERO dummy records...")

service_modules = [
    ("auth", "services.auth_service.main"),
    ("hr", "services.hr_service.main"),
    ("crm", "services.crm_service.main"),
    ("finance", "services.finance_service.main"),
    ("inventory", "services.inventory_service.main"),
    ("procurement", "services.procurement_service.main"),
    ("projects", "services.projects_service.main"),
    ("support", "services.support_service.main"),
    ("marketing", "services.marketing_service.main"),
    ("collaboration", "services.collaboration_service.main"),
    ("compliance", "services.compliance_service.main"),
    ("automation", "services.automation_service.main"),
    ("ai_copilot", "services.ai_copilot_service.main"),
]

import importlib
for name, mod_path in service_modules:
    try:
        mod = importlib.import_module(mod_path)
        on_startup = getattr(mod, "on_startup", None)
        if on_startup:
            on_startup()
        print(f"  [OK] Initialized {name}")
    except Exception as e:
        print(f"  [FAIL] Error initializing {name}: {e}")

print("\nVerifying Table Row Counts across all databases:")
import sqlite3
all_clean = True
total_records_summary = {}

for db_path in sorted(glob.glob(os.path.join(data_dir, "*.db"))):
    db_name = os.path.basename(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
    counts = {}
    for t in tables:
        cnt = cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        if cnt > 0:
            counts[t] = cnt
    total_records_summary[db_name] = counts
    print(f"  {db_name:25} -> {counts}")

print("\nValidation Checklist:")
print(f"  - Employees in hr.db          : {total_records_summary.get('hr.db', {}).get('hr_employees', 0)} (must be 0)")
print(f"  - Leads in crm.db             : {total_records_summary.get('crm.db', {}).get('crm_leads', 0)} (must be 0)")
print(f"  - Deals in crm.db             : {total_records_summary.get('crm.db', {}).get('crm_deals', 0)} (must be 0)")
print(f"  - Contacts in crm.db          : {total_records_summary.get('crm.db', {}).get('crm_contacts', 0)} (must be 0)")
print(f"  - Companies in crm.db         : {total_records_summary.get('crm.db', {}).get('crm_companies', 0)} (must be 0)")
print(f"  - Invoices in finance.db      : {total_records_summary.get('finance.db', {}).get('fin_invoices', 0)} (must be 0)")
print(f"  - Products in inventory.db    : {total_records_summary.get('inventory.db', {}).get('inv_products', 0)} (must be 0)")
print(f"  - Projects in projects.db     : {total_records_summary.get('projects.db', {}).get('prj_projects', 0)} (must be 0)")
print(f"  - Tasks in projects.db        : {total_records_summary.get('projects.db', {}).get('prj_tasks', 0)} (must be 0)")
print(f"  - Tickets in support.db       : {total_records_summary.get('support.db', {}).get('sup_tickets', 0)} (must be 0)")
print(f"  - POs in procurement.db       : {total_records_summary.get('procurement.db', {}).get('proc_purchase_orders', 0)} (must be 0)")
print(f"  - Campaigns in marketing.db   : {total_records_summary.get('marketing.db', {}).get('marketing_campaigns', 0)} (must be 0)")
print(f"  - Messages in collaboration.db: {total_records_summary.get('collaboration.db', {}).get('collab_messages', 0)} (must be 0)")
print(f"  - Admin Users in auth.db      : {total_records_summary.get('auth.db', {}).get('users', 0)} (must be 1: admin@acroflow.enterprise)")
print(f"  - Organizations in auth.db    : {total_records_summary.get('auth.db', {}).get('organizations', 0)} (must be 1: org-acroflow-main)")
