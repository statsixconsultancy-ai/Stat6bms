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

from services.auth_service.models import Organization, User, Role, AuthAuditLog
from services.auth_service.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserCreateRequest,
    UserResponse
)
from services.auth_service.seed import seed_auth_data

config = get_service_config("auth-service", default_port=8001, db_filename="auth.db")
db_mgr = create_db_manager(config.database_url)

app = FastAPI(
    title="BMS Auth & Identity Microservice",
    description="Multi-Tenancy, User Provisioning, RBAC & Authentication Engine",
    version="2.0.0"
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
    return {"service": "auth-service", "status": "UP", "port": config.service_port}

@app.post("/webhooks/events")
async def receive_event(event: dict):
    """Receive cross-process domain event forwarded from the Gateway."""
    return {"status": "received", "event_name": event.get("event_name")}

# ----------------------------------------------------
# 2. Authentication & Tenant Lifecycle Endpoints
# ----------------------------------------------------
@app.post("/auth/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Provision a new multi-tenant organization and initial superuser."""
    existing_org = db.query(Organization).filter_by(slug=req.org_slug).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Organization with slug '{req.org_slug}' already exists."
        )

    existing_user = db.query(User).filter_by(email=req.admin_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{req.admin_email}' already registered."
        )

    org = Organization(
        name=req.org_name,
        slug=req.org_slug
    )
    db.add(org)
    db.flush()

    user = User(
        org_id=org.id,
        email=req.admin_email,
        full_name=req.admin_name,
        password_hash=hash_password(req.password),
        role="superadmin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(org)

    # Publish distributed event
    await event_bus.publish("tenant.provisioned", {"org_id": org.id, "name": org.name, "admin_email": user.email})

    token = create_access_token({
        "sub": user.id,
        "org_id": org.id,
        "role": user.role,
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
        "email": user.email
    })

    return TokenResponse(
        access_token=token,
        expires_in_minutes=config.jwt_access_token_expire_minutes,
        user=user.to_dict(),
        organization=org.to_dict() if org else {"id": user.org_id, "name": "Default"}
    )

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
            "full_name": "Authenticated Member",
            "email": user_ctx.email,
            "organization": org.to_dict() if org else {"id": user_ctx.org_id, "name": "AcroFlow"}
        }

    return {
        "user": user.to_dict(),
        "organization": org.to_dict() if org else None
    }

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
            avatar_url=u.avatar_url,
            is_active=u.is_active
        )
        for u in users
    ]
