from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class RegisterRequest(BaseModel):
    org_name: str
    org_slug: str
    admin_name: str
    admin_email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

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

class UserResponse(BaseModel):
    id: str
    org_id: str
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
