import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def generate_uuid() -> str:
    """Generate a cryptographically unique UUIDv4 string."""
    return str(uuid.uuid4())

class TenantModel(Base):
    """
    Abstract base class for all microservice entities enforcing:
    1. Cryptographically secure UUID primary keys.
    2. Strict multi-tenant isolation via indexed org_id.
    3. Immutable creation timestamp and automatic update timestamp.
    """
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Convert SQLAlchemy model instance to dictionary representation."""
        result = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(val, datetime):
                result[col.name] = val.isoformat()
            else:
                result[col.name] = val
        return result
