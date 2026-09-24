import uuid
from sqlalchemy.orm import Session
from services.crm_service.models import Company, Contact, Lead, Deal, Quote, QuoteItem

def seed_crm_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds initial commercial enterprise accounts, leads, deals, and quotations."""
    # Check if data already exists
    if session.query(Company).filter_by(org_id=org_id).first():
        return

    # 1. Companies
    c1 = Company(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Quantum Dynamics Corp",
        industry="Quantum Computing & AI",
        website="https://quantumdynamics.internal",
        phone="+1 (555) 234-8901",
        address="100 Silicon Way, Palo Alto, CA",
        annual_revenue=15000000.0,
        tier="Tier 1",
        account_owner="Sarah Connor"
    )
    c2 = Company(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Nexus Robotics Systems",
        industry="Autonomous Robotics",
        website="https://nexusrobotics.internal",
        phone="+1 (555) 345-9012",
        address="450 Automaton Blvd, Boston, MA",
        annual_revenue=28000000.0,
        tier="Tier 1",
        account_owner="Marcus Reed"
    )
    c3 = Company(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Apex Biometrics Global",
        industry="Identity Security",
        website="https://apexbiometrics.internal",
        phone="+1 (555) 456-0123",
        address="789 Cyber Park, Austin, TX",
        annual_revenue=8500000.0,
        tier="Tier 2",
        account_owner="Elena Rostova"
    )
    session.add_all([c1, c2, c3])
    session.flush()

    # 2. Contacts
    ct1 = Contact(
        id=str(uuid.uuid4()),
        org_id=org_id,
        company_id=c1.id,
        first_name="Eleanor",
        last_name="Vance",
        email="eleanor@quantumdynamics.internal",
        phone="+1 (555) 234-8902",
        job_title="Chief Technology Officer",
        is_primary=True
    )
    ct2 = Contact(
        id=str(uuid.uuid4()),
        org_id=org_id,
        company_id=c2.id,
        first_name="David",
        last_name="Zhang",
        email="dzhang@nexusrobotics.internal",
        phone="+1 (555) 345-9013",
        job_title="VP of Procurement",
        is_primary=True
    )
    ct3 = Contact(
        id=str(uuid.uuid4()),
        org_id=org_id,
        company_id=c3.id,
        first_name="Liam",
        last_name="O'Connor",
        email="liam@apexbiometrics.internal",
        phone="+1 (555) 456-0124",
        job_title="Chief Information Security Officer",
        is_primary=True
    )
    session.add_all([ct1, ct2, ct3])
    session.flush()

    # 3. Leads
    l1 = Lead(
        id=str(uuid.uuid4()),
        org_id=org_id,
        first_name="Maya",
        last_name="Lin",
        email="maya.lin@starlightbio.internal",
        phone="+1 (555) 789-1122",
        company_name="Starlight Genomics",
        status="Qualified",
        source="Website",
        score=85,
        assigned_to="Sarah Connor",
        notes="Urgent enterprise requirement for automated genome sequencing data management."
    )
    l2 = Lead(
        id=str(uuid.uuid4()),
        org_id=org_id,
        first_name="Lucas",
        last_name="Vance",
        email="lucas@orbitsatellites.internal",
        phone="+1 (555) 890-2233",
        company_name="Orbit Satellites Inc",
        status="Contacted",
        source="Campaign",
        score=72,
        assigned_to="Marcus Reed",
        notes="Expressed strong interest during Q3 webinar on satellite telemetry analytics."
    )
    l3 = Lead(
        id=str(uuid.uuid4()),
        org_id=org_id,
        first_name="Sophie",
        last_name="Martin",
        email="smartin@cyberguard.internal",
        phone="+1 (555) 901-3344",
        company_name="CyberGuard Networks",
        status="New",
        source="Inbound Form",
        score=95,
        assigned_to="Elena Rostova",
        notes="High-priority inbound lead requesting immediate custom pricing."
    )
    session.add_all([l1, l2, l3])

    # 4. Deals
    d1 = Deal(
        id=str(uuid.uuid4()),
        org_id=org_id,
        company_id=c1.id,
        contact_id=ct1.id,
        title="Enterprise Quantum Cloud Cluster",
        amount=250000.0,
        stage="Negotiation",
        probability=80,
        close_date="2026-11-15",
        owner="Sarah Connor"
    )
    d2 = Deal(
        id=str(uuid.uuid4()),
        org_id=org_id,
        company_id=c2.id,
        contact_id=ct2.id,
        title="Autonomous Drone Fleet Licensing",
        amount=450000.0,
        stage="Won",
        probability=100,
        close_date="2026-09-10",
        owner="Marcus Reed"
    )
    d3 = Deal(
        id=str(uuid.uuid4()),
        org_id=org_id,
        company_id=c3.id,
        contact_id=ct3.id,
        title="Zero Trust Biometric Upgrade",
        amount=125000.0,
        stage="Proposal Sent",
        probability=60,
        close_date="2026-12-01",
        owner="Elena Rostova"
    )
    session.add_all([d1, d2, d3])
    session.flush()

    # 5. Quotes
    q1 = Quote(
        id=str(uuid.uuid4()),
        org_id=org_id,
        quote_number="QTE-2026-001",
        deal_id=d2.id,
        company_id=c2.id,
        status="Accepted",
        subtotal=450000.0,
        tax_rate=0.08,
        tax_amount=36000.0,
        discount_amount=0.0,
        total_amount=486000.0,
        valid_until="2026-10-31"
    )
    session.add(q1)
    session.flush()

    qi1 = QuoteItem(
        id=str(uuid.uuid4()),
        org_id=org_id,
        quote_id=q1.id,
        description="Autonomous Drone Navigation OS Fleet License (50 Units)",
        quantity=50,
        unit_price=8000.0,
        total_price=400000.0
    )
    qi2 = QuoteItem(
        id=str(uuid.uuid4()),
        org_id=org_id,
        quote_id=q1.id,
        description="Enterprise SLA 24/7 Dedicated Mission Control Support",
        quantity=1,
        unit_price=50000.0,
        total_price=50000.0
    )
    session.add_all([qi1, qi2])
    session.commit()
