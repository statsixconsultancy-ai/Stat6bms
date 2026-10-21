from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Integer, ForeignKey
from common.models import Base, TenantModel, generate_uuid

# The 7 canonical STAT6 user personas
USER_PERSONAS = [
    "ADMIN",         # Superuser & organization administrator
    "EMPLOYEE",      # Internal staff with departmental access
    "MANAGER",       # Department lead with approval & reporting rights
    "CUSTOMER",      # External client portal (Quotes, Invoices, Support)
    "VENDOR",        # External supplier portal (KYC, RFQs, POs, Bills)
    "PARTNER",       # Channel reseller / agency partner portal
    "EXTERNAL_USER"  # Temporary auditor, freelancer, or contractor
]

DEFAULT_ENABLED_MODULES = [
    "crm", "marketing", "projects", "hr", "finance",
    "inventory", "procurement", "support", "analytics",
    "collaboration", "compliance", "automation", "ai", "admin"
]

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    industry = Column(String(100), default="Technology")
    currency = Column(String(10), default="USD")
    timezone = Column(String(50), default="UTC")
    plan = Column(String(50), default="Enterprise")
    
    # Advanced Multi-Entity, Branch & Localization Configuration
    branches = Column(JSON, default=list) # e.g. [{"code": "HQ", "name": "Headquarters", "gstin": "29AAAAA0000A1Z5", "city": "Bengaluru"}]
    tax_identifiers = Column(JSON, default=dict) # e.g. {"gstin": "...", "pan": "...", "vat": "..."}
    fiscal_year_start = Column(Integer, default=4) # 4 = April (India/UK), 1 = January (US/Global)
    white_label_domain = Column(String(255), nullable=True)
    branding_logo_url = Column(String(500), nullable=True)
    
    # Feature Toggles: enable or disable any of the 14 modules per organization
    enabled_modules = Column(JSON, default=lambda: list(DEFAULT_ENABLED_MODULES))
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "industry": self.industry,
            "currency": self.currency,
            "timezone": self.timezone,
            "plan": self.plan,
            "branches": self.branches or [],
            "tax_identifiers": self.tax_identifiers or {},
            "fiscal_year_start": self.fiscal_year_start or 4,
            "white_label_domain": self.white_label_domain,
            "branding_logo_url": self.branding_logo_url,
            "enabled_modules": self.enabled_modules or list(DEFAULT_ENABLED_MODULES),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class User(TenantModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    
    # Role & Persona mapping
    role = Column(String(50), default="admin") # admin, manager, member, auditor
    persona = Column(String(50), default="ADMIN") # ADMIN, EMPLOYEE, MANAGER, CUSTOMER, VENDOR, PARTNER, EXTERNAL_USER
    
    # Portal profile (maps external users to their company/vendor/partner identity)
    portal_profile = Column(JSON, default=dict) # {"entity_id": "...", "portal_type": "CUSTOMER", "permissions": [...]}
    
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(100), nullable=True)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self):
        d = super().to_dict()
        d.pop("password_hash", None)
        d.pop("mfa_secret", None)
        return d

class Role(TenantModel):
    __tablename__ = "roles"

    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    persona = Column(String(50), default="EMPLOYEE")
    permissions = Column(JSON, default=list) # e.g. ["crm:*", "projects:read", "finance:view_invoices"]
    field_level_security = Column(JSON, default=dict) # e.g. {"hr.employee": ["hidden:salary", "masked:ssn"]}

class CustomFieldDefinition(TenantModel):
    """
    STAT6 Dynamic Custom Field Engine (Zoho Creator Alternative)
    Allows adding custom attributes to any module without altering underlying SQL schemas.
    """
    __tablename__ = "custom_field_definitions"

    module_name = Column(String(50), nullable=False, index=True) # e.g. crm, finance, hr, projects
    entity_type = Column(String(50), nullable=False, index=True) # e.g. Deal, Lead, Employee, Invoice
    field_name = Column(String(100), nullable=False) # technical key e.g. 'custom_pan_number'
    field_label = Column(String(100), nullable=False) # display label e.g. 'PAN / Tax Identification'
    field_type = Column(String(50), nullable=False) # text, number, currency, date, select, multiselect, lookup, formula
    options = Column(JSON, nullable=True) # list of choices for select/multiselect
    is_required = Column(Boolean, default=False)
    default_value = Column(String(255), nullable=True)

class CustomObject(TenantModel):
    """
    STAT6 Low-Code Custom Table Builder (Matching Zoho Creator)
    Allows organizations to provision dynamic business tables with auto-generated CRUD APIs.
    """
    __tablename__ = "custom_objects"

    object_name = Column(String(100), nullable=False, index=True) # e.g. 'flight_charters', 'clinical_trials'
    display_name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    schema_definition = Column(JSON, default=dict) # JSON Schema defining attributes & validation rules
    records_count = Column(Integer, default=0)


class CustomObjectRecord(TenantModel):
    """
    Stores dynamic JSON rows for any user-defined CustomObject table.
    """
    __tablename__ = "custom_object_records"

    object_id = Column(String(36), nullable=False, index=True)
    object_name = Column(String(100), nullable=False, index=True)
    record_data = Column(JSON, default=dict)
    created_by = Column(String(255), default="admin@acroflow.enterprise")


class AuthAuditLog(TenantModel):
    __tablename__ = "auth_audit_logs"

    actor_id = Column(String(36), nullable=True)
    actor_name = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False) # LOGIN, LOGOUT, REGISTER, ROLE_CHANGE, MFA_VERIFY
    ip_address = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)

