import uuid
from sqlalchemy.orm import Session
from services.finance_service.models import Invoice, InvoiceItem, Payment, Expense, JournalEntry, JournalLine

def seed_finance_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds invoices, payments, operating expenses, and initial double-entry balanced ledger."""
    if session.query(Invoice).filter_by(org_id=org_id).first():
        return

    # 1. Invoices
    inv1 = Invoice(
        id=str(uuid.uuid4()),
        org_id=org_id,
        invoice_number="INV-2026-001",
        client_name="Nexus Robotics Systems",
        issue_date="2026-09-01",
        due_date="2026-10-01",
        status="Paid",
        subtotal=450000.0,
        tax_amount=0.0,
        total_amount=450000.0,
        balance_due=0.0
    )
    inv2 = Invoice(
        id=str(uuid.uuid4()),
        org_id=org_id,
        invoice_number="INV-2026-002",
        client_name="Quantum Dynamics Corp",
        issue_date="2026-09-15",
        due_date="2026-10-15",
        status="Sent",
        subtotal=125000.0,
        tax_amount=0.0,
        total_amount=125000.0,
        balance_due=125000.0
    )
    inv3 = Invoice(
        id=str(uuid.uuid4()),
        org_id=org_id,
        invoice_number="INV-2026-003",
        client_name="Apex Biometrics Global",
        issue_date="2026-09-20",
        due_date="2026-10-20",
        status="Sent",
        subtotal=75000.0,
        tax_amount=0.0,
        total_amount=75000.0,
        balance_due=75000.0
    )
    session.add_all([inv1, inv2, inv3])
    session.flush()

    # Invoice Items
    item1 = InvoiceItem(
        id=str(uuid.uuid4()),
        org_id=org_id,
        invoice_id=inv1.id,
        description="Autonomous Drone Navigation OS Fleet License",
        quantity=1,
        unit_price=450000.0,
        total_price=450000.0
    )
    item2 = InvoiceItem(
        id=str(uuid.uuid4()),
        org_id=org_id,
        invoice_id=inv2.id,
        description="Quantum Cloud Security Gateway Implementation",
        quantity=1,
        unit_price=125000.0,
        total_price=125000.0
    )
    session.add_all([item1, item2])

    # Payment for Inv 1
    pmt1 = Payment(
        id=str(uuid.uuid4()),
        org_id=org_id,
        invoice_id=inv1.id,
        amount=450000.0,
        payment_date="2026-09-10",
        payment_method="Wire Transfer",
        reference_number="WIRE-US-992144"
    )
    session.add(pmt1)

    # 2. Operating Expenses
    exp1 = Expense(
        id=str(uuid.uuid4()),
        org_id=org_id,
        category="Cloud Hosting & Infrastructure",
        vendor="Amazon Web Services (AWS)",
        amount=18450.0,
        date="2026-09-05",
        status="Paid",
        approved_by="Elena Rostova"
    )
    exp2 = Expense(
        id=str(uuid.uuid4()),
        org_id=org_id,
        category="Software Subscriptions",
        vendor="Datadog APM & Security Monitoring",
        amount=4200.0,
        date="2026-09-12",
        status="Paid",
        approved_by="Marcus Chen"
    )
    exp3 = Expense(
        id=str(uuid.uuid4()),
        org_id=org_id,
        category="Software Subscriptions",
        vendor="GitHub Enterprise & Copilot Fleet",
        amount=3600.0,
        date="2026-09-15",
        status="Paid",
        approved_by="Marcus Chen"
    )
    session.add_all([exp1, exp2, exp3])

    # 3. Double-Entry Journal Entries
    j1 = JournalEntry(
        id=str(uuid.uuid4()),
        org_id=org_id,
        entry_number="JRN-001",
        date="2026-09-01",
        description="Initial Enterprise Capital Contribution",
        reference_type="CAPITAL",
        reference_id="TREASURY-01",
        total_debit=1000000.0,
        total_credit=1000000.0,
        is_balanced=True
    )
    session.add(j1)
    session.flush()

    jl1_1 = JournalLine(id=str(uuid.uuid4()), org_id=org_id, journal_entry_id=j1.id, account_code="1010", account_name="Operating Cash & Bank", debit=1000000.0, credit=0.0)
    jl1_2 = JournalLine(id=str(uuid.uuid4()), org_id=org_id, journal_entry_id=j1.id, account_code="3000", account_name="Owner / Paid-in Capital", debit=0.0, credit=1000000.0)
    session.add_all([jl1_1, jl1_2])

    j2 = JournalEntry(
        id=str(uuid.uuid4()),
        org_id=org_id,
        entry_number="JRN-002",
        date="2026-09-10",
        description="Payment Received for Invoice INV-2026-001 (Nexus Robotics)",
        reference_type="INVOICE_PAYMENT",
        reference_id=inv1.id,
        total_debit=450000.0,
        total_credit=450000.0,
        is_balanced=True
    )
    session.add(j2)
    session.flush()

    jl2_1 = JournalLine(id=str(uuid.uuid4()), org_id=org_id, journal_entry_id=j2.id, account_code="1010", account_name="Operating Cash & Bank", debit=450000.0, credit=0.0)
    jl2_2 = JournalLine(id=str(uuid.uuid4()), org_id=org_id, journal_entry_id=j2.id, account_code="1200", account_name="Accounts Receivable", debit=0.0, credit=450000.0)
    session.add_all([jl2_1, jl2_2])

    session.commit()
