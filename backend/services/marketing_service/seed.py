import uuid
from sqlalchemy.orm import Session
from services.marketing_service.models import Campaign, LandingPage, LeadForm, UTMTracking

def seed_marketing_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds high-performing marketing campaigns, landing pages, forms, and UTM channel data."""
    if session.query(Campaign).filter_by(org_id=org_id).first():
        return

    # 1. Campaigns
    cmp1 = Campaign(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Autonomous Cloud Infrastructure Ads",
        type="Paid Search",
        status="Active",
        budget=60000.0,
        actual_spend=52000.0,
        attributed_revenue=480000.0,
        start_date="2026-07-01",
        end_date="2026-12-31",
        target_audience="VPs of Engineering, Cloud Architects"
    )
    cmp2 = Campaign(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Q3 Global Enterprise Summit",
        type="Webinar",
        status="Active",
        budget=45000.0,
        actual_spend=41200.0,
        attributed_revenue=340000.0,
        start_date="2026-08-01",
        end_date="2026-10-31",
        target_audience="Chief Technology Officers, Operations Directors"
    )
    cmp3 = Campaign(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="C-Suite LinkedIn Executive Inbound",
        type="Social",
        status="Active",
        budget=35000.0,
        actual_spend=31500.0,
        attributed_revenue=290000.0,
        start_date="2026-06-15",
        end_date="2026-12-31",
        target_audience="CEOs, Managing Partners, CFOs"
    )
    session.add_all([cmp1, cmp2, cmp3])
    session.flush()

    # 2. Landing Pages
    lp1 = LandingPage(
        id=str(uuid.uuid4()),
        org_id=org_id,
        campaign_id=cmp1.id,
        title="Next-Gen Enterprise BMS Demo",
        slug="enterprise-bms-demo",
        views_count=14200,
        conversions_count=620,
        bounce_rate=0.28
    )
    lp2 = LandingPage(
        id=str(uuid.uuid4()),
        org_id=org_id,
        campaign_id=cmp2.id,
        title="Cloud ERP Replacement Guide & Benchmark",
        slug="cloud-erp-benchmark",
        views_count=9800,
        conversions_count=430,
        bounce_rate=0.32
    )
    session.add_all([lp1, lp2])

    # 3. Lead Forms
    lf1 = LeadForm(
        id=str(uuid.uuid4()),
        org_id=org_id,
        campaign_id=cmp1.id,
        name="Book VIP Executive Demo Form",
        fields_config='["first_name", "last_name", "email", "phone", "company_name"]',
        is_active=True
    )
    lf2 = LeadForm(
        id=str(uuid.uuid4()),
        org_id=org_id,
        campaign_id=cmp2.id,
        name="Whitepaper Download & Evaluation Access",
        fields_config='["first_name", "last_name", "email", "company_name"]',
        is_active=True
    )
    session.add_all([lf1, lf2])

    # 4. UTM Channel Attribution
    utm1 = UTMTracking(
        id=str(uuid.uuid4()),
        org_id=org_id,
        source="google",
        medium="cpc",
        campaign_name="autonomous_cloud_ads",
        clicks=8400,
        conversions=420,
        spend=32000.0
    )
    utm2 = UTMTracking(
        id=str(uuid.uuid4()),
        org_id=org_id,
        source="linkedin",
        medium="paid",
        campaign_name="csuite_inbound",
        clicks=4200,
        conversions=290,
        spend=21000.0
    )
    session.add_all([utm1, utm2])
    session.commit()
