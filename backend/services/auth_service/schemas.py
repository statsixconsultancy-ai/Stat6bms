from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class RegisterRequest(BaseModel):
    org_name: Optional[str] = None
    org_slug: Optional[str] = None
    admin_name: Optional[str] = None
    admin_email: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    password: str
    persona: str = "ADMIN"
    currency: Optional[str] = "USD"
    timezone: Optional[str] = "UTC"
    contract_accepted: bool = True
    contract_version: Optional[str] = "v2.4-enterprise-msa"

class LoginRequest(BaseModel):
    email: str
    password: str

class OAuthTokenRequest(BaseModel):
    grant_type: str = "password"
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    scope: Optional[str] = "read write"

class OAuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str = "read write"
    user: Dict[str, Any]
    persona: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: Dict[str, Any]
    organization: Dict[str, Any]

class UserCreateRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: str = "member"
    persona: str = "EMPLOYEE" # ADMIN, EMPLOYEE, MANAGER, CUSTOMER, VENDOR, PARTNER, EXTERNAL_USER
    phone: Optional[str] = None
    portal_profile: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: str
    org_id: str
    email: str
    full_name: str
    role: str
    persona: str = "EMPLOYEE"
    phone: Optional[str] = None
    portal_profile: Optional[Dict[str, Any]] = None
    avatar_url: Optional[str] = None
    is_active: bool

class OrganizationSettingsUpdateRequest(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    branches: Optional[List[Dict[str, Any]]] = None
    tax_identifiers: Optional[Dict[str, Any]] = None
    fiscal_year_start: Optional[int] = None
    white_label_domain: Optional[str] = None
    branding_logo_url: Optional[str] = None
    enabled_modules: Optional[List[str]] = None

class CustomFieldCreateRequest(BaseModel):
    module_name: str
    entity_type: str
    field_name: str
    field_label: str
    field_type: str = "text" # text, number, currency, date, select, multiselect, lookup, formula
    options: Optional[List[str]] = None
    is_required: bool = False
    default_value: Optional[str] = None

class CustomFieldResponse(BaseModel):
    id: str
    org_id: str
    module_name: str
    entity_type: str
    field_name: str
    field_label: str
    field_type: str
    options: Optional[List[str]] = None
    is_required: bool
    default_value: Optional[str] = None

class CustomObjectCreateRequest(BaseModel):
    object_name: str
    display_name: str
    description: Optional[str] = None
    schema_definition: Dict[str, Any] = {}

class CustomObjectResponse(BaseModel):
    id: str
    org_id: str
    object_name: str
    display_name: str
    description: Optional[str] = None
    schema_definition: Dict[str, Any]
    records_count: int


class CustomObjectRecordCreateRequest(BaseModel):
    record_data: Dict[str, Any]


class CustomObjectRecordResponse(BaseModel):
    id: str
    org_id: str
    object_id: str
    object_name: str
    record_data: Dict[str, Any]
    created_by: Optional[str] = None
    created_at: Optional[str] = None

