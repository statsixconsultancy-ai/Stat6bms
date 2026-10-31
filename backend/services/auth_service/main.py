import os
import sys
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.config import get_service_config
from common.database import create_db_manager
from common.models import Base
from common.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_context,
    UserContext
)
from common.middleware import setup_microservice_middleware
from common.event_bus import event_bus

from services.auth_service.models import (
    Organization,
    User,
    Role,
    AuthAuditLog,
    CustomFieldDefinition,
    CustomObject,
    CustomObjectRecord,
    USER_PERSONAS,
    DEFAULT_ENABLED_MODULES
)
from services.auth_service.schemas import (
    RegisterRequest,
    LoginRequest,
    OAuthTokenRequest,
    OAuthTokenResponse,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
    OrganizationSettingsUpdateRequest,
    CustomFieldCreateRequest,
    CustomFieldResponse,
    CustomObjectCreateRequest,
    CustomObjectResponse,
    CustomObjectRecordCreateRequest,
    CustomObjectRecordResponse
)
from services.auth_service.seed import seed_auth_data

config = get_service_config("auth-service", default_port=8001, db_filename="auth.db")
db_mgr = create_db_manager(config.database_url)

app = FastAPI(
    title="STAT6 Auth & Multi-Persona Identity Engine",
    description="Multi-Tenancy, 7 User Personas, RBAC, Custom Fields & Admin Settings",
    version="2.4.0"
)

setup_microservice_middleware(app, "auth-service", config.cors_origins)

db_mgr.init_tables(Base)

@app.on_event("startup")
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_auth_data(session)
    finally:
        session.close()

def get_db():
    yield from db_mgr.get_session()

# ----------------------------------------------------
# 1. Health & Webhook Endpoints
# ----------------------------------------------------
@app.get("/health")
def health():
    return {
        "service": "auth-service",
        "status": "UP",
        "port": config.service_port,
        "personas_supported": USER_PERSONAS,
        "default_modules": len(DEFAULT_ENABLED_MODULES)
    }

@app.post("/webhooks/events")
async def receive_event(event: dict):
    """Receive cross-process domain event forwarded from the Gateway."""
    return {"status": "received", "event_name": event.get("event_name")}

# ----------------------------------------------------
# 2. Authentication & Tenant Lifecycle Endpoints
# ----------------------------------------------------
@app.post("/auth/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Provision a new multi-tenant organization and initial superuser, or register a user into the primary tenant."""
    target_email = (req.admin_email or req.email or "").strip()
    if not target_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is required."
        )
    target_name = (req.admin_name or req.full_name or target_email.split("@")[0]).strip()

    existing_user = db.query(User).filter_by(email=target_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{target_email}' already registered."
        )

    if req.org_slug:
        existing_org = db.query(Organization).filter_by(slug=req.org_slug).first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Organization with slug '{req.org_slug}' already exists."
            )
        org = Organization(
            name=req.org_name or req.org_slug,
            slug=req.org_slug,
            currency=req.currency or "USD",
            timezone=req.timezone or "UTC"
        )
        db.add(org)
        db.flush()
        target_role = req.role or "superadmin"
    else:
        org = db.query(Organization).filter_by(id="org-acroflow-main").first()
        if not org:
            org = db.query(Organization).first()
        if not org:
            org = Organization(
                id="org-acroflow-main",
                name=req.org_name or "STAT6 Enterprise Corp",
                slug="stat6-enterprise",
                currency=req.currency or "USD",
                timezone=req.timezone or "UTC"
            )
            db.add(org)
            db.flush()
        target_role = req.role or "admin"

    user = User(
        org_id=org.id,
        email=target_email,
        full_name=target_name,
        password_hash=hash_password(req.password),
        role=target_role,
        persona=req.persona if req.persona in USER_PERSONAS else "ADMIN"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(org)

    # Publish distributed event
    await event_bus.publish("tenant.provisioned", {
        "org_id": org.id,
        "name": org.name,
        "admin_email": user.email,
        "persona": user.persona
    })

    token = create_access_token({
        "sub": user.id,
        "org_id": org.id,
        "role": user.role,
        "persona": user.persona,
        "email": user.email
    })

    return TokenResponse(
        access_token=token,
        expires_in_minutes=config.jwt_access_token_expire_minutes,
        user=user.to_dict(),
        organization=org.to_dict()
    )

@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Verify credentials and issue JWT access token."""
    user = db.query(User).filter_by(email=req.email, is_active=True).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    org = db.query(Organization).filter_by(id=user.org_id).first()
    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token({
        "sub": user.id,
        "org_id": user.org_id,
        "role": user.role,
        "persona": user.persona or "EMPLOYEE",
        "email": user.email
    })

    return TokenResponse(
        access_token=token,
        expires_in_minutes=config.jwt_access_token_expire_minutes,
        user=user.to_dict(),
        organization=org.to_dict() if org else {"id": user.org_id, "name": "Default"}
    )

@app.post("/auth/oauth/token", response_model=OAuthTokenResponse)
@app.post("/oauth/token", response_model=OAuthTokenResponse)
def oauth_token(req: OAuthTokenRequest, db: Session = Depends(get_db)):
    """
    Native RFC 6749 OAuth 2.0 Token Endpoint.
    Zero external dependencies: issues cryptographically signed JWT bearer tokens
    with RBAC claims, persona, and tenant isolation scopes.
    """
    login_id = req.username or req.email
    if not login_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing username or email for OAuth grant."
        )

    user = db.query(User).filter_by(email=login_id, is_active=True).first()
    if not user or not req.password or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OAuth credentials or inactive account."
        )

    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token({
        "sub": user.id,
        "org_id": user.org_id,
        "role": user.role,
        "persona": user.persona or "EMPLOYEE",
        "email": user.email,
        "scope": req.scope or "read write"
    })

    return OAuthTokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=config.jwt_access_token_expire_minutes * 60,
        scope=req.scope or "read write",
        user=user.to_dict(),
        persona=user.persona or "EMPLOYEE",
        role=user.role or "member"
    )

@app.get("/auth/oauth/userinfo")
@app.get("/oauth/userinfo")
def oauth_userinfo(
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Native OpenID / OAuth 2.0 UserInfo Endpoint."""
    user = db.query(User).filter_by(id=user_ctx.user_id).first()
    if not user:
        return {
            "sub": user_ctx.user_id,
            "email": user_ctx.email,
            "role": user_ctx.role,
            "persona": "EMPLOYEE",
            "org_id": user_ctx.org_id
        }
    return {
        "sub": user.id,
        "email": user.email,
        "name": user.full_name,
        "role": user.role,
        "persona": user.persona,
        "org_id": user.org_id,
        "is_active": user.is_active
    }

@app.get("/auth/me")
def get_current_user_profile(
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Retrieve full profile of the authenticated user and organization."""
    user = db.query(User).filter_by(id=user_ctx.user_id).first()
    org = db.query(Organization).filter_by(id=user_ctx.org_id).first() if user else None

    if not user:
        return {
            "id": user_ctx.user_id,
            "org_id": user_ctx.org_id,
            "role": user_ctx.role,
            "persona": "EMPLOYEE",
            "full_name": "Authenticated Member",
            "email": user_ctx.email,
            "organization": org.to_dict() if org else {"id": user_ctx.org_id, "name": "STAT6 Platform"}
        }

    return {
        "user": user.to_dict(),
        "organization": org.to_dict() if org else None
    }

# ----------------------------------------------------
# 3. Personas & Multi-User Provisioning
# ----------------------------------------------------
@app.get("/auth/personas")
def get_user_personas():
    """Returns metadata for all 7 supported STAT6 user personas."""
    return [
        {
            "persona": "ADMIN",
            "label": "Administrator",
            "description": "Full access to Organization Setup, RBAC, Billing, Module Toggles & System Audit",
            "portal_type": "INTERNAL"
        },
        {
            "persona": "EMPLOYEE",
            "label": "Internal Staff",
            "description": "Role-scoped access to operational modules, Employee Self-Service, Attendance & Tasks",
            "portal_type": "INTERNAL"
        },
        {
            "persona": "MANAGER",
            "label": "Department Manager",
            "description": "Team oversight, Resource Capacity planner, multi-tier approvals & KPI dashboards",
            "portal_type": "INTERNAL"
        },
        {
            "persona": "CUSTOMER",
            "label": "Customer / Client",
            "description": "External Customer Portal: View/E-sign proposals, pay invoices, track project tasks & support tickets",
            "portal_type": "EXTERNAL_PORTAL"
        },
        {
            "persona": "VENDOR",
            "label": "Supplier / Vendor",
            "description": "External Vendor Portal: KYC onboarding, submit RFQ bids, acknowledge POs, submit vendor bills",
            "portal_type": "EXTERNAL_PORTAL"
        },
        {
            "persona": "PARTNER",
            "label": "Channel Partner / Reseller",
            "description": "External Partner Portal: Register partner deals, co-selling collateral, commission statements",
            "portal_type": "EXTERNAL_PORTAL"
        },
        {
            "persona": "EXTERNAL_USER",
            "label": "External Guest / Auditor",
            "description": "Time-boxed record-level guest access for external financial auditors, legal counsel, or contractors",
            "portal_type": "GUEST"
        }
    ]

@app.get("/auth/users", response_model=list[UserResponse])
def list_tenant_users(
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """List all team members inside the current tenant."""
    users = db.query(User).filter_by(org_id=user_ctx.org_id).all()
    return [
        UserResponse(
            id=u.id,
            org_id=u.org_id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            persona=u.persona or "EMPLOYEE",
            phone=u.phone,
            portal_profile=u.portal_profile,
            avatar_url=u.avatar_url,
            is_active=u.is_active
        )
        for u in users
    ]

@app.post("/auth/users", response_model=UserResponse)
def create_tenant_user(
    req: UserCreateRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Provision a new user under a specific Persona."""
    existing = db.query(User).filter_by(org_id=user_ctx.org_id, email=req.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists in organization.")
    
    user = User(
        org_id=user_ctx.org_id,
        email=req.email,
        full_name=req.full_name,
        password_hash=hash_password(req.password),
        role=req.role,
        persona=req.persona if req.persona in USER_PERSONAS else "EMPLOYEE",
        phone=req.phone,
        portal_profile=req.portal_profile or {}
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        org_id=user.org_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        persona=user.persona,
        phone=user.phone,
        portal_profile=user.portal_profile,
        avatar_url=user.avatar_url,
        is_active=user.is_active
    )

# ----------------------------------------------------
# 4. Organization Settings & Module Configuration
# ----------------------------------------------------
@app.get("/auth/organization/settings")
def get_org_settings(
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Retrieve full organization profile, branches, tax info, and active module toggles."""
    org = db.query(Organization).filter_by(id=user_ctx.org_id).first()
    if not org:
        org = db.query(Organization).first()
    if not org:
        org = Organization(id=user_ctx.org_id, name="STAT6 Main Org", slug="stat6-main")
        db.add(org)
        db.commit()
    return org.to_dict()

@app.put("/auth/organization/settings")
def update_org_settings(
    req: OrganizationSettingsUpdateRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Update organization multi-branch setup, tax IDs, fiscal calendar, or toggle modules."""
    org = db.query(Organization).filter_by(id=user_ctx.org_id).first()
    if not org:
        org = db.query(Organization).first()
    if not org:
        org = Organization(id=user_ctx.org_id, name="STAT6 Main Org", slug="stat6-main")
        db.add(org)
        db.flush()
    
    if req.name is not None:
        org.name = req.name
    if req.industry is not None:
        org.industry = req.industry
    if req.currency is not None:
        org.currency = req.currency
    if req.timezone is not None:
        org.timezone = req.timezone
    if req.branches is not None:
        org.branches = req.branches
    if req.tax_identifiers is not None:
        org.tax_identifiers = req.tax_identifiers
    if req.fiscal_year_start is not None:
        org.fiscal_year_start = req.fiscal_year_start
    if req.white_label_domain is not None:
        org.white_label_domain = req.white_label_domain
    if req.branding_logo_url is not None:
        org.branding_logo_url = req.branding_logo_url
    if req.enabled_modules is not None:
        org.enabled_modules = req.enabled_modules

    db.commit()
    db.refresh(org)
    return org.to_dict()

# ----------------------------------------------------
# 5. Dynamic Custom Fields Engine (Zoho Creator Alt)
# ----------------------------------------------------
@app.get("/auth/custom-fields", response_model=list[CustomFieldResponse])
def list_custom_fields(
    module_name: str = None,
    entity_type: str = None,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Retrieve custom fields configured for an entity type or module."""
    query = db.query(CustomFieldDefinition).filter_by(org_id=user_ctx.org_id)
    if module_name:
        query = query.filter_by(module_name=module_name)
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    fields = query.all()
    return [
        CustomFieldResponse(
            id=f.id,
            org_id=f.org_id,
            module_name=f.module_name,
            entity_type=f.entity_type,
            field_name=f.field_name,
            field_label=f.field_label,
            field_type=f.field_type,
            options=f.options,
            is_required=f.is_required,
            default_value=f.default_value
        )
        for f in fields
    ]

@app.post("/auth/custom-fields", response_model=CustomFieldResponse)
def create_custom_field(
    req: CustomFieldCreateRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Define a new custom attribute on a business entity."""
    field = CustomFieldDefinition(
        org_id=user_ctx.org_id,
        module_name=req.module_name,
        entity_type=req.entity_type,
        field_name=req.field_name,
        field_label=req.field_label,
        field_type=req.field_type,
        options=req.options or [],
        is_required=req.is_required,
        default_value=req.default_value
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    return CustomFieldResponse(
        id=field.id,
        org_id=field.org_id,
        module_name=field.module_name,
        entity_type=field.entity_type,
        field_name=field.field_name,
        field_label=field.field_label,
        field_type=field.field_type,
        options=field.options,
        is_required=field.is_required,
        default_value=field.default_value
    )

@app.delete("/auth/custom-fields/{field_id}")
def delete_custom_field(
    field_id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    field = db.query(CustomFieldDefinition).filter_by(id=field_id, org_id=user_ctx.org_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Custom field definition not found.")
    db.delete(field)
    db.commit()
    return {"status": "deleted", "field_id": field_id}

# ----------------------------------------------------
# 6. Low-Code Custom Objects Builder
# ----------------------------------------------------
@app.get("/auth/custom-objects", response_model=list[CustomObjectResponse])
def list_custom_objects(
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    objects = db.query(CustomObject).filter_by(org_id=user_ctx.org_id).all()
    return [
        CustomObjectResponse(
            id=o.id,
            org_id=o.org_id,
            object_name=o.object_name,
            display_name=o.display_name,
            description=o.description,
            schema_definition=o.schema_definition or {},
            records_count=o.records_count or 0
        )
        for o in objects
    ]

@app.post("/auth/custom-objects", response_model=CustomObjectResponse)
def create_custom_object(
    req: CustomObjectCreateRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    obj = CustomObject(
        org_id=user_ctx.org_id,
        object_name=req.object_name,
        display_name=req.display_name,
        description=req.description,
        schema_definition=req.schema_definition or {},
        records_count=0
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return CustomObjectResponse(
        id=obj.id,
        org_id=obj.org_id,
        object_name=obj.object_name,
        display_name=obj.display_name,
        description=obj.description,
        schema_definition=obj.schema_definition or {},
        records_count=0
    )


@app.get("/auth/custom-objects/{object_id}/records", response_model=list[CustomObjectRecordResponse])
def list_custom_object_records(
    object_id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    obj = db.query(CustomObject).filter(
        (CustomObject.id == object_id) | (CustomObject.object_name == object_id),
        CustomObject.org_id == user_ctx.org_id
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Custom object not found")

    records = db.query(CustomObjectRecord).filter_by(
        org_id=user_ctx.org_id,
        object_id=obj.id
    ).order_by(CustomObjectRecord.created_at.desc()).all()

    return [
        CustomObjectRecordResponse(
            id=r.id,
            org_id=r.org_id,
            object_id=r.object_id,
            object_name=r.object_name,
            record_data=r.record_data or {},
            created_by=r.created_by,
            created_at=r.created_at.isoformat() if r.created_at else None
        )
        for r in records
    ]


@app.post("/auth/custom-objects/{object_id}/records", response_model=CustomObjectRecordResponse)
def create_custom_object_record(
    object_id: str,
    req: CustomObjectRecordCreateRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    obj = db.query(CustomObject).filter(
        (CustomObject.id == object_id) | (CustomObject.object_name == object_id),
        CustomObject.org_id == user_ctx.org_id
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Custom object not found")

    rec = CustomObjectRecord(
        org_id=user_ctx.org_id,
        object_id=obj.id,
        object_name=obj.object_name,
        record_data=req.record_data or {},
        created_by=user_ctx.email or "admin@acroflow.enterprise"
    )
    db.add(rec)
    obj.records_count = (obj.records_count or 0) + 1
    db.commit()
    db.refresh(rec)

    return CustomObjectRecordResponse(
        id=rec.id,
        org_id=rec.org_id,
        object_id=rec.object_id,
        object_name=rec.object_name,
        record_data=rec.record_data or {},
        created_by=rec.created_by,
        created_at=rec.created_at.isoformat() if rec.created_at else None
    )


@app.delete("/auth/custom-objects/records/{record_id}")
def delete_custom_object_record(
    record_id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    rec = db.query(CustomObjectRecord).filter_by(id=record_id, org_id=user_ctx.org_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Custom object record not found")

    obj = db.query(CustomObject).filter_by(id=rec.object_id, org_id=user_ctx.org_id).first()
    if obj and (obj.records_count or 0) > 0:
        obj.records_count -= 1

    db.delete(rec)
    db.commit()
    return {"status": "deleted", "record_id": record_id}

