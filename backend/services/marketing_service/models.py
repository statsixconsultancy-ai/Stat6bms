import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class Campaign(TenantModel):
    __tablename__ = "marketing_campaigns"

    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), default="Paid Search")  # Email, Paid Search, Social, Webinar, Partner
    status = Column(String(50), default="Active", index=True)  # Active, Scheduled, Completed, Draft
    budget = Column(Float, default=0.0)
    actual_spend = Column(Float, default=0.0)
    attributed_revenue = Column(Float, default=0.0)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    target_audience = Column(String(255), default="Enterprise B2B Decision Makers")

    landing_pages = relationship("LandingPage", back_populates="campaign", cascade="all, delete-orphan")
    forms = relationship("LeadForm", back_populates="campaign", cascade="all, delete-orphan")

class LandingPage(TenantModel):
    __tablename__ = "marketing_landing_pages"

    campaign_id = Column(String(36), ForeignKey("marketing_campaigns.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    views_count = Column(Integer, default=0)
    conversions_count = Column(Integer, default=0)
    bounce_rate = Column(Float, default=0.35)

    campaign = relationship("Campaign", back_populates="landing_pages")

class LeadForm(TenantModel):
    __tablename__ = "marketing_lead_forms"

    campaign_id = Column(String(36), ForeignKey("marketing_campaigns.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    fields_config = Column(Text, default='["first_name", "last_name", "email", "phone", "company_name"]')
    is_active = Column(Boolean, default=True)

    campaign = relationship("Campaign", back_populates="forms")
    submissions = relationship("FormSubmission", back_populates="form")

class FormSubmission(TenantModel):
    __tablename__ = "marketing_form_submissions"

    form_id = Column(String(36), ForeignKey("marketing_lead_forms.id"), nullable=True, index=True)
    campaign_id = Column(String(36), nullable=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    form = relationship("LeadForm", back_populates="submissions")

class UTMTracking(TenantModel):
    __tablename__ = "marketing_utm_tracking"

    source = Column(String(100), nullable=False, index=True)      # google, linkedin, twitter, newsletter
    medium = Column(String(100), nullable=False)                  # cpc, organic, email, referral
    campaign_name = Column(String(255), nullable=False, index=True)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)

class DripJourney(TenantModel):
    __tablename__ = "marketing_drip_journeys"

    name = Column(String(255), nullable=False, index=True)
    trigger_event = Column(String(100), default="lead.captured", index=True)  # lead.captured, quote.sent, deal.created
    steps_config = Column(Text, default='[{"step": 1, "channel": "email", "delay_hours": 0, "template": "Welcome"}, {"step": 2, "channel": "whatsapp", "delay_hours": 48, "template": "Demo Invite"}]')
    is_active = Column(Boolean, default=True)
    enrolled_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)

class BroadcastCampaign(TenantModel):
    __tablename__ = "marketing_broadcasts"

    name = Column(String(255), nullable=False, index=True)
    channel = Column(String(50), default="email")  # email, sms, whatsapp
    target_segment = Column(String(255), default="All Leads")
    message_template = Column(Text, nullable=False)
    scheduled_at = Column(String(50), nullable=True)
    status = Column(String(50), default="Draft", index=True)  # Draft, Scheduled, Sent
    recipient_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)

