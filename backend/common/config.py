import os
from pydantic import BaseModel
from typing import List, Optional

try:
    from dotenv import load_dotenv
    BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(BACKEND_DIR, ".env"))
except ImportError:
    BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BACKEND_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

class ServiceConfig(BaseModel):
    service_name: str = "bms-service"
    service_port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = True
    database_url: str = f"sqlite:///{os.path.join(DATA_DIR, 'service.db')}"
    jwt_secret_key: str = os.getenv("BMS_JWT_SECRET", "bms-super-secret-enterprise-key-2026")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24 # 24 hours
    gateway_url: str = os.getenv("BMS_GATEWAY_URL", "http://localhost:8000")
    gateway_secret: str = os.getenv("BMS_GATEWAY_SECRET", "bms-internal-gateway-secret-2026")
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
    event_bus_backend: str = os.getenv("BMS_EVENT_BUS", "relay") # relay, memory, or redis
    redis_url: Optional[str] = os.getenv("BMS_REDIS_URL", "redis://localhost:6379/0")
    supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
    supabase_key: Optional[str] = os.getenv("SUPABASE_KEY")

def get_service_config(
    service_name: str,
    default_port: int,
    db_filename: str
) -> ServiceConfig:
    """Helper to generate standardized config for any of the BMS microservices with centralized data paths."""
    default_db_path = os.path.join(DATA_DIR, db_filename)
    service_env_var = f"BMS_{service_name.upper().replace('-', '_')}_DB_URL"
    master_db_url = os.getenv("SUPABASE_DB_URL", os.getenv("DATABASE_URL"))
    
    db_url = os.getenv(service_env_var, master_db_url or f"sqlite:///{default_db_path}")
    port = int(os.getenv(f"BMS_{service_name.upper().replace('-', '_')}_PORT", default_port))
    
    return ServiceConfig(
        service_name=service_name,
        service_port=port,
        database_url=db_url,
        debug=os.getenv("BMS_DEBUG", "true").lower() == "true"
    )
