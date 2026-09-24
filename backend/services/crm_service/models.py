import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class Company(TenantModel):
    __tablename__ = "crm_companies"

    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100), default="Technology")
    website = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    annual_revenue = Column(Float, default=0.0)
    tier = Column(String(50), default="Tier 2")  # Tier 1, Tier 2, Tier 3
    account_owner = Column(String(255), default="Sales Lead")

    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="company")

class Contact(TenantModel):
    __tablename__ = "crm_contacts"

    company_id = Column(String(36), ForeignKey("crm_companies.id"), nullable=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    job_title = Column(String(100), default="Executive")
    is_primary = Column(Boolean, default=False)

    company = relationship("Company", back_populates="contacts")
    deals = relationship("Deal", back_populates="contact")

class Lead(TenantModel):
    __tablename__ = "crm_leads"

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    company_name = Column(String(255), nullable=False)
    status = Column(String(50), default="New", index=True)  # New, Contacted, Qualified, Converted, Disqualified
    source = Column(String(100), default="Website")  # Website, Inbound Form, Referral, Partner, Campaign
    score = Column(Integer, default=50)
    assigned_to = Column(String(255), default="Sales Rep")
    notes = Column(Text, nullable=True)

class Deal(TenantModel):
    __tablename__ = "crm_deals"

    title = Column(String(255), nullable=False)
    company_id = Column(String(36), ForeignKey("crm_companies.id"), nullable=True, index=True)
    contact_id = Column(String(36), ForeignKey("crm_contacts.id"), nullable=True, index=True)
    amount = Column(Float, default=0.0, index=True)
    stage = Column(String(50), default="Prospecting", index=True)  # Prospecting, Qualification, Proposal Sent, Negotiation, Won, Lost
    probability = Column(Integer, default=20)  # 0 to 100
    close_date = Column(String(50), nullable=True)
    owner = Column(String(255), default="Account Executive")

    company = relationship("Company", back_populates="deals")
    contact = relationship("Contact", back_populates="deals")
    quotes = relationship("Quote", back_populates="deal")

class Quote(TenantModel):
    __tablename__ = "crm_quotes"

    quote_number = Column(String(50), nullable=False, unique=True, index=True)
    deal_id = Column(String(36), ForeignKey("crm_deals.id"), nullable=True, index=True)
    company_id = Column(String(36), ForeignKey("crm_companies.id"), nullable=True, index=True)
    status = Column(String(50), default="Draft")  # Draft, Sent, Accepted, Declined
    subtotal = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.08)  # 8% standard
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    valid_until = Column(String(50), nullable=True)

    deal = relationship("Deal", back_populates="quotes")
    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")

class QuoteItem(TenantModel):
    __tablename__ = "crm_quote_items"

    quote_id = Column(String(36), ForeignKey("crm_quotes.id"), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)

    quote = relationship("Quote", back_populates="items")
