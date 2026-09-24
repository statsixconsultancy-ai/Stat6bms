import os
import sys
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
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

from services.crm_service.models import Company, Contact, Lead, Deal, Quote, QuoteItem
from services.crm_service.schemas import (
    LeadCreate, LeadUpdate, LeadResponse,
    LeadConvertRequest, LeadConvertResponse,
    CompanyCreate, CompanyResponse, CompanyDetailResponse,
    ContactCreate, ContactResponse,
    DealCreate, DealUpdate, StageUpdateRequest, DealResponse,
    QuoteCreate, QuoteResponse, QuoteItemResponse,
    CRMSummaryResponse
)
from services.crm_service.seed import seed_crm_data

config = get_service_config("crm-service", default_port=8002, db_filename="crm.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="BMS Commercial Engine — Sales & CRM Microservice",
    description="Pipeline Management, Deal Velocity, Lead Conversion, Account 360 & Quotations",
    version="2.0.0"
)

setup_microservice_middleware(app, "crm-service", config.cors_origins)

@app.on_event("startup")
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_crm_data(session)
    finally:
        session.close()

def get_db():
    yield from db_mgr.get_session()

# ----------------------------------------------------
# 1. Health & Webhooks
# ----------------------------------------------------
@app.get("/health")
def health():
    return {"service": "crm-service", "status": "UP", "port": config.service_port}

@app.post("/webhooks/events")
async def handle_incoming_events(event: dict, db: Session = Depends(get_db)):
    """Receives cross-service distributed events (e.g., marketing lead captured)."""
    event_name = event.get("event_name")
    payload = event.get("payload", {})
    org_id = event.get("org_id", "org-acroflow-main")

    if event_name == "lead.captured":
        # Automatically ingest lead from marketing campaign or web form
        new_lead = Lead(
            id=str(uuid.uuid4()),
            org_id=org_id,
            first_name=payload.get("first_name", "Web"),
            last_name=payload.get("last_name", "Inbound"),
            email=payload.get("email", f"web-{uuid.uuid4().hex[:6]}@domain.internal"),
            phone=payload.get("phone"),
            company_name=payload.get("company_name", "Web Discovery Lead"),
            status="New",
            source=payload.get("source", "Marketing Inbound"),
            score=75,
            notes=f"Captured via form: {payload.get('form_name', 'Default Form')}"
        )
        db.add(new_lead)
        db.commit()
        return {"status": "lead_ingested", "lead_id": new_lead.id}

    return {"status": "ignored", "event_name": event_name}

# ----------------------------------------------------
# 2. Leads Endpoints
# ----------------------------------------------------
@app.get("/crm/leads", response_model=List[LeadResponse])
def list_leads(
    status: Optional[str] = None,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    query = db.query(Lead).filter_by(org_id=user_ctx.org_id)
    if status:
        query = query.filter_by(status=status)
    leads = query.order_by(Lead.created_at.desc()).all()
    return [LeadResponse(**l.to_dict()) for l in leads]

@app.post("/crm/leads", response_model=LeadResponse)
async def create_lead(
    req: LeadCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    lead = Lead(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email,
        phone=req.phone,
        company_name=req.company_name,
        status="New",
        source=req.source or "Direct",
        score=req.score or 50,
        assigned_to=req.assigned_to or "Sales Rep",
        notes=req.notes
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    await event_bus.publish("lead.created", {"lead_id": lead.id, "email": lead.email, "company": lead.company_name}, org_id=user_ctx.org_id)
    return LeadResponse(**lead.to_dict())

@app.get("/crm/leads/{id}", response_model=LeadResponse)
def get_lead(id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    lead = db.query(Lead).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse(**lead.to_dict())

@app.post("/crm/leads/{id}/convert", response_model=LeadConvertResponse)
async def convert_lead(
    id: str,
    req: LeadConvertRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Atomic transaction:
    1. Mark lead as 'Converted'.
    2. Provision new Company account.
    3. Provision primary Contact.
    4. Provision initial Deal opportunity.
    5. Emit 'lead.converted' event.
    """
    lead = db.query(Lead).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.status == "Converted":
        raise HTTPException(status_code=400, detail="Lead has already been converted")

    lead.status = "Converted"

    # Create Company
    company = Company(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        name=lead.company_name,
        industry="Technology",
        tier="Tier 2",
        account_owner=user_ctx.email or "Account Executive"
    )
    db.add(company)
    db.flush()

    # Create Contact
    contact = Contact(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        company_id=company.id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        email=lead.email,
        phone=lead.phone,
        job_title="Executive Sponsor",
        is_primary=True
    )
    db.add(contact)
    db.flush()

    # Create Deal
    deal_title = req.deal_title or f"{lead.company_name} - Enterprise Solution"
    deal_amount = req.deal_amount if req.deal_amount is not None else 50000.0
    deal = Deal(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        company_id=company.id,
        contact_id=contact.id,
        title=deal_title,
        amount=deal_amount,
        stage="Qualification",
        probability=40,
        close_date=req.close_date or "2026-12-31",
        owner=user_ctx.email or "Account Executive"
    )
    db.add(deal)
    db.commit()

    # Publish distributed event
    await event_bus.publish("lead.converted", {
        "lead_id": lead.id,
        "company_id": company.id,
        "company_name": company.name,
        "contact_id": contact.id,
        "deal_id": deal.id,
        "amount": deal.amount
    }, org_id=user_ctx.org_id)

    return LeadConvertResponse(
        message="Lead converted successfully to Company, Contact, and Deal",
        lead_id=lead.id,
        company_id=company.id,
        company_name=company.name,
        contact_id=contact.id,
        deal_id=deal.id,
        deal_title=deal.title,
        deal_amount=deal.amount
    )

# ----------------------------------------------------
# 3. Companies & Contacts Endpoints
# ----------------------------------------------------
@app.get("/crm/companies", response_model=List[CompanyResponse])
def list_companies(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    companies = db.query(Company).filter_by(org_id=user_ctx.org_id).order_by(Company.name.asc()).all()
    return [CompanyResponse(**c.to_dict()) for c in companies]

@app.get("/crm/companies/{id}", response_model=CompanyDetailResponse)
def get_company_detail(id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    contacts = [ContactResponse(**ct.to_dict()) for ct in company.contacts]
    deals = company.deals
    total_val = sum(d.amount for d in deals)

    return CompanyDetailResponse(
        **company.to_dict(),
        contacts=contacts,
        deals_count=len(deals),
        total_deal_value=total_val
    )

@app.post("/crm/companies", response_model=CompanyResponse)
def create_company(req: CompanyCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    company = Company(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        name=req.name,
        industry=req.industry or "Technology",
        website=req.website,
        phone=req.phone,
        address=req.address,
        annual_revenue=req.annual_revenue or 0.0,
        tier=req.tier or "Tier 2",
        account_owner=req.account_owner or "Sales Lead"
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return CompanyResponse(**company.to_dict())

@app.get("/crm/contacts", response_model=List[ContactResponse])
def list_contacts(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    contacts = db.query(Contact).filter_by(org_id=user_ctx.org_id).all()
    return [ContactResponse(**ct.to_dict()) for ct in contacts]

@app.post("/crm/contacts", response_model=ContactResponse)
def create_contact(req: ContactCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    contact = Contact(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        company_id=req.company_id,
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email,
        phone=req.phone,
        job_title=req.job_title or "Executive",
        is_primary=req.is_primary or False
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return ContactResponse(**contact.to_dict())

# ----------------------------------------------------
# 4. Deals & Pipeline Endpoints
# ----------------------------------------------------
@app.get("/crm/deals", response_model=List[DealResponse])
def list_deals(
    stage: Optional[str] = None,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    query = db.query(Deal).filter_by(org_id=user_ctx.org_id)
    if stage:
        query = query.filter_by(stage=stage)
    deals = query.order_by(Deal.amount.desc()).all()
    
    result = []
    for d in deals:
        c_name = d.company.name if d.company else "Standalone Account"
        d_dict = d.to_dict()
        d_dict["company_name"] = c_name
        result.append(DealResponse(**d_dict))
    return result

@app.post("/crm/deals", response_model=DealResponse)
async def create_deal(
    req: DealCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    deal = Deal(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        title=req.title,
        company_id=req.company_id,
        contact_id=req.contact_id,
        amount=req.amount,
        stage=req.stage or "Prospecting",
        probability=req.probability or 20,
        close_date=req.close_date or "2026-12-31",
        owner=req.owner or "Account Executive"
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)

    company_name = deal.company.name if deal.company else "Direct Account"
    d_dict = deal.to_dict()
    d_dict["company_name"] = company_name

    await event_bus.publish("deal.created", {"deal_id": deal.id, "title": deal.title, "amount": deal.amount}, org_id=user_ctx.org_id)
    return DealResponse(**d_dict)

@app.patch("/crm/deals/{id}/stage", response_model=DealResponse)
async def update_deal_stage(
    id: str,
    req: StageUpdateRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Transitions deal stage along the pipeline.
    If transitioned to 'Won', automatically broadcasts 'deal.won' domain event.
    """
    deal = db.query(Deal).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    old_stage = deal.stage
    deal.stage = req.stage
    if req.probability is not None:
        deal.probability = req.probability
    elif req.stage.lower() == "won":
        deal.probability = 100
    elif req.stage.lower() == "lost":
        deal.probability = 0

    db.commit()
    db.refresh(deal)

    company_name = deal.company.name if deal.company else "AcroFlow Account"

    # Broadcast deal.won event across microservices
    if deal.stage.lower() == "won" and old_stage.lower() != "won":
        await event_bus.publish("deal.won", {
            "deal_id": deal.id,
            "title": deal.title,
            "amount": deal.amount,
            "company_id": deal.company_id,
            "company_name": company_name,
            "org_id": user_ctx.org_id
        }, org_id=user_ctx.org_id)

    d_dict = deal.to_dict()
    d_dict["company_name"] = company_name
    return DealResponse(**d_dict)

# ----------------------------------------------------
# 5. Quotes Endpoints
# ----------------------------------------------------
@app.get("/crm/quotes", response_model=List[QuoteResponse])
def list_quotes(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    quotes = db.query(Quote).filter_by(org_id=user_ctx.org_id).order_by(Quote.created_at.desc()).all()
    results = []
    for q in quotes:
        items = [QuoteItemResponse(**i.to_dict()) for i in q.items]
        q_dict = q.to_dict()
        q_dict["items"] = items
        results.append(QuoteResponse(**q_dict))
    return results

@app.post("/crm/quotes", response_model=QuoteResponse)
def create_quote(
    req: QuoteCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    # Automated calculation
    subtotal = sum(i.quantity * i.unit_price for i in req.items)
    tax_rate = 0.08
    tax_amount = round(subtotal * tax_rate, 2)
    discount = 0.0
    total = round(subtotal + tax_amount - discount, 2)

    seq = int(datetime.utcnow().timestamp()) % 100000
    quote_number = f"QTE-2026-{seq:05d}"

    quote = Quote(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        quote_number=quote_number,
        deal_id=req.deal_id,
        company_id=req.company_id,
        status="Draft",
        subtotal=subtotal,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        discount_amount=discount,
        total_amount=total,
        valid_until=req.valid_until or "2026-12-31"
    )
    db.add(quote)
    db.flush()

    items = []
    for it in req.items:
        qi = QuoteItem(
            id=str(uuid.uuid4()),
            org_id=user_ctx.org_id,
            quote_id=quote.id,
            description=it.description,
            quantity=it.quantity,
            unit_price=it.unit_price,
            total_price=it.quantity * it.unit_price
        )
        db.add(qi)
        items.append(qi)

    db.commit()
    db.refresh(quote)

    q_dict = quote.to_dict()
    q_dict["items"] = [QuoteItemResponse(**it.to_dict()) for it in items]
    return QuoteResponse(**q_dict)

# ----------------------------------------------------
# 6. Executive Pipeline Summary
# ----------------------------------------------------
@app.get("/crm/summary", response_model=CRMSummaryResponse)
def get_crm_summary(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    deals = db.query(Deal).filter_by(org_id=user_ctx.org_id).all()
    leads = db.query(Lead).filter_by(org_id=user_ctx.org_id).all()

    total_pipeline = sum(d.amount for d in deals if d.stage.lower() != "lost")
    won_deals = [d for d in deals if d.stage.lower() == "won"]
    won_revenue = sum(d.amount for d in won_deals)
    win_rate = (len(won_deals) / len(deals) * 100.0) if deals else 0.0

    qualified_leads = [l for l in leads if l.status in ["Qualified", "Converted"]]

    return CRMSummaryResponse(
        total_pipeline_value=total_pipeline,
        total_deals_count=len(deals),
        won_revenue=won_revenue,
        win_rate_percent=round(win_rate, 1),
        leads_count=len(leads),
        qualified_leads_count=len(qualified_leads)
    )
