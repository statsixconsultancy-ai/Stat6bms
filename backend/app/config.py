import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "BMS - Business Management System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./bms.db"
    SECRET_KEY: str = "supersecret_bms_jwt_key_for_development_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

settings = Settings()
