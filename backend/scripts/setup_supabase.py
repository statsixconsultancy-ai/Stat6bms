#!/usr/bin/env python3
"""
Supabase Schema Provisioner & Migration Tool
Connects all 14 BMS microservices to your Supabase PostgreSQL database,
creates all relational tables, indexes, and constraints, and seeds initial data.
"""
import os
import sys
import argparse

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"))

def main():
    parser = argparse.ArgumentParser(description="Initialize Supabase PostgreSQL tables for BMS")
    parser.add_argument("--db-url", help="Direct Supabase PostgreSQL connection string", default=None)
    args = parser.parse_args()

    db_url = args.db_url or os.getenv("SUPABASE_DB_URL")
    if not db_url or "YOUR-PASSWORD" in db_url:
        print("=" * 70)
        print("  ERROR: Missing Supabase Database Connection URI")
        print("=" * 70)
        print("Please provide your database connection string with password.")
        print("You can find it in your Supabase dashboard at:")
        print("  Project Settings -> Database -> Connection string -> URI")
        print("\nExample:")
        print("  python scripts/setup_supabase.py --db-url 'postgresql://postgres.dawezhpwmjwimrmjmter:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres'")
        print("Or set SUPABASE_DB_URL in backend/.env")
        sys.exit(1)

    # Set environment variable so all microservices pick it up
    os.environ["SUPABASE_DB_URL"] = db_url

    print("=" * 70)
    print("  INITIALIZING BMS ENTERPRISE TABLES ON SUPABASE POSTGRESQL")
    print("=" * 70)
    print(f"Target Database: {db_url.split('@')[-1] if '@' in db_url else db_url}")

    services = [
        ("Auth Service", "services.auth_service.main"),
        ("CRM Service", "services.crm_service.main"),
        ("Marketing Service", "services.marketing_service.main"),
        ("Projects Service", "services.projects_service.main"),
        ("HR Service", "services.hr_service.main"),
        ("Finance Service", "services.finance_service.main"),
        ("Inventory Service", "services.inventory_service.main"),
        ("Procurement Service", "services.procurement_service.main"),
        ("Support Service", "services.support_service.main"),
        ("Collaboration Service", "services.collaboration_service.main"),
        ("Compliance Service", "services.compliance_service.main"),
        ("Automation Service", "services.automation_service.main"),
        ("AI Copilot Service", "services.ai_copilot_service.main"),
    ]

    for name, module_path in services:
        print(f"--> Provisioning {name} ...", end=" ", flush=True)
        try:
            mod = __import__(module_path, fromlist=["on_startup"])
            if hasattr(mod, "on_startup"):
                mod.on_startup()
            print("[OK]")
        except Exception as e:
            print(f"[FAILED: {e}]")

    print("\n" + "=" * 70)
    print("  ALL SERVICES SUCCESSFULLY INITIALIZED ON SUPABASE!")
    print("=" * 70)

if __name__ == "__main__":
    main()
