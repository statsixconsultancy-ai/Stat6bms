import os
import sys
import uuid
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.config import get_service_config
from common.database import create_db_manager
from common.models import Base
from common.security import get_user_context, UserContext
from common.middleware import setup_microservice_middleware
from common.event_bus import event_bus

from services.marketing_service.models import Campaign, LandingPage, LeadForm, FormSubmission, UTMTracking
from services.marketing_service.schemas import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    LandingPageCreate, LandingPageResponse,
    LeadFormCreate, LeadFormResponse,
    PublicFormSubmitRequest, FormSubmissionResponse,
    UTMTrackingResponse, MarketingROIResponse
)
from services.marketing_service.seed import seed_marketing_data

config = get_service_config("marketing-service", default_port=8003, db_filename="marketing.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="BMS Marketing Intelligence Microservice",
    description="Campaign Tracking, Inbound Web Lead Capture, Channel Attribution & Real-Time ROI Engine",
    version="2.0.0"
)

setup_microservice_middleware(app, "marketing-service", config.cors_origins)

@app.on_event("startup")
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_marketing_data(session)
    finally:
        session.close()

def get_db():
    yield from db_mgr.get_session()

# ----------------------------------------------------
# 1. Health & Webhook Endpoints
# ----------------------------------------------------
@app.get("/health")
def health():
    return {"service": "marketing-service", "status": "UP", "port": config.service_port}

@app.post("/webhooks/events")
async def handle_events(event: dict, db: Session = Depends(get_db)):
    """Handles external events (e.g. deal.won to attribute closed-won revenue to campaigns)."""
    event_name = event.get("event_name")
    payload = event.get("payload", {})
    if event_name == "deal.won":
        amount = payload.get("amount", 0.0)
        # Attribute revenue to first active campaign
        first_cmp = db.query(Campaign).filter_by(status="Active").first()
        if first_cmp and amount > 0:
            first_cmp.attributed_revenue += amount
            db.commit()
            return {"status": "attributed", "campaign": first_cmp.name, "amount": amount}
    return {"status": "ignored", "event_name": event_name}

# ----------------------------------------------------
# 2. Campaigns Endpoints
# ----------------------------------------------------
@app.get("/marketing/campaigns", response_model=List[CampaignResponse])
def list_campaigns(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).filter_by(org_id=user_ctx.org_id).order_by(Campaign.created_at.desc()).all()
    results = []
    for c in campaigns:
        roi = ((c.attributed_revenue - c.actual_spend) / c.actual_spend * 100.0) if c.actual_spend > 0 else 0.0
        c_dict = c.to_dict()
        c_dict["roi_percent"] = round(roi, 1)
        results.append(CampaignResponse(**c_dict))
    return results

@app.post("/marketing/campaigns", response_model=CampaignResponse)
def create_campaign(
    req: CampaignCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    campaign = Campaign(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        name=req.name,
        type=req.type or "Paid Search",
        status=req.status or "Active",
        budget=req.budget,
        actual_spend=req.actual_spend,
        attributed_revenue=req.attributed_revenue,
        start_date=req.start_date,
        end_date=req.end_date,
        target_audience=req.target_audience or "Enterprise B2B Decision Makers"
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    roi = ((campaign.attributed_revenue - campaign.actual_spend) / campaign.actual_spend * 100.0) if campaign.actual_spend > 0 else 0.0
    c_dict = campaign.to_dict()
    c_dict["roi_percent"] = round(roi, 1)
    return CampaignResponse(**c_dict)

@app.get("/marketing/campaigns/{id}", response_model=CampaignResponse)
def get_campaign(id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    c = db.query(Campaign).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    roi = ((c.attributed_revenue - c.actual_spend) / c.actual_spend * 100.0) if c.actual_spend > 0 else 0.0
    c_dict = c.to_dict()
    c_dict["roi_percent"] = round(roi, 1)
    return CampaignResponse(**c_dict)

# ----------------------------------------------------
# 3. Landing Pages & Lead Forms
# ----------------------------------------------------
@app.get("/marketing/landing-pages", response_model=List[LandingPageResponse])
def list_landing_pages(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    pages = db.query(LandingPage).filter_by(org_id=user_ctx.org_id).all()
    results = []
    for p in pages:
        cr = (p.conversions_count / p.views_count * 100.0) if p.views_count > 0 else 0.0
        p_dict = p.to_dict()
        p_dict["conversion_rate_percent"] = round(cr, 2)
        results.append(LandingPageResponse(**p_dict))
    return results

@app.post("/marketing/landing-pages", response_model=LandingPageResponse)
def create_landing_page(
    req: LandingPageCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    page = LandingPage(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        campaign_id=req.campaign_id,
        title=req.title,
        slug=req.slug,
        views_count=0,
        conversions_count=0,
        bounce_rate=0.30
    )
    db.add(page)
    db.commit()
    db.refresh(page)
    p_dict = page.to_dict()
    p_dict["conversion_rate_percent"] = 0.0
    return LandingPageResponse(**p_dict)

@app.get("/marketing/forms", response_model=List[LeadFormResponse])
def list_forms(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    forms = db.query(LeadForm).filter_by(org_id=user_ctx.org_id).all()
    return [LeadFormResponse(**f.to_dict()) for f in forms]

# ----------------------------------------------------
# 4. Public Web Inbound Form Intake
# ----------------------------------------------------
@app.post("/marketing/public/submit-form", response_model=FormSubmissionResponse)
async def submit_public_lead_form(req: PublicFormSubmitRequest, db: Session = Depends(get_db)):
    """
    Publicly accessible intake endpoint for web forms.
    Records submission, increments campaign conversion metrics,
    and publishes 'lead.captured' event to the distributed event bus.
    """
    org_id = "org-acroflow-main"
    sub_id = str(uuid.uuid4())

    sub = FormSubmission(
        id=sub_id,
        org_id=org_id,
        form_id=req.form_id,
        campaign_id=req.campaign_id,
        email=req.email,
        first_name=req.first_name,
        last_name=req.last_name,
        company_name=req.company_name,
        phone=req.phone,
        utm_source=req.utm_source,
        utm_medium=req.utm_medium,
        utm_campaign=req.utm_campaign,
        notes=req.notes
    )
    db.add(sub)

    # Update UTM attribution counts if matched
    if req.utm_source and req.utm_campaign:
        utm = db.query(UTMTracking).filter_by(
            org_id=org_id,
            source=req.utm_source.lower()
        ).first()
        if utm:
            utm.conversions += 1

    db.commit()

    # Publish distributed event across microservices
    await event_bus.publish("lead.captured", {
        "first_name": req.first_name,
        "last_name": req.last_name,
        "email": req.email,
        "phone": req.phone,
        "company_name": req.company_name,
        "source": f"{req.utm_source} / {req.utm_medium}",
        "form_id": req.form_id,
        "submission_id": sub_id
    }, org_id=org_id)

    return FormSubmissionResponse(
        id=sub_id,
        form_id=req.form_id,
        campaign_id=req.campaign_id,
        email=req.email,
        first_name=req.first_name,
        last_name=req.last_name,
        company_name=req.company_name,
        status="received",
        message="Submission received and lead captured successfully."
    )

# ----------------------------------------------------
# 5. Marketing Analytics & Channel ROI
# ----------------------------------------------------
@app.get("/marketing/analytics/roi", response_model=MarketingROIResponse)
def get_marketing_roi(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).filter_by(org_id=user_ctx.org_id).all()
    total_spend = sum(c.actual_spend for c in campaigns)
    total_rev = sum(c.attributed_revenue for c in campaigns)
    blended_roi = ((total_rev - total_spend) / total_spend * 100.0) if total_spend > 0 else 0.0

    submissions_count = db.query(FormSubmission).filter_by(org_id=user_ctx.org_id).count()
    active_count = sum(1 for c in campaigns if c.status == "Active")
    blended_cac = (total_spend / submissions_count) if submissions_count > 0 else 0.0

    return MarketingROIResponse(
        total_campaigns=len(campaigns),
        active_campaigns=active_count,
        total_marketing_spend=round(total_spend, 2),
        total_attributed_revenue=round(total_rev, 2),
        blended_roi_percent=round(blended_roi, 1),
        total_conversions=submissions_count,
        blended_cac=round(blended_cac, 2)
    )

@app.get("/marketing/utm", response_model=List[UTMTrackingResponse])
def list_utm_channels(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    utm_records = db.query(UTMTracking).filter_by(org_id=user_ctx.org_id).all()
    return [UTMTrackingResponse(**u.to_dict()) for u in utm_records]
