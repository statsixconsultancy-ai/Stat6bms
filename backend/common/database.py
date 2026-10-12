from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from common.models import Base

class DatabaseManager:
    """Encapsulates engine creation and session generation per microservice."""
    
    def __init__(self, database_url: str):
        # Normalize postgres:// to postgresql:// for Supabase compatibility
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        self.database_url = database_url
        is_sqlite = database_url.startswith("sqlite")
        
        if is_sqlite:
            # SQLite configuration for local microservice databases
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool if ":memory:" in database_url else None
            )
        else:
            # PostgreSQL configuration with connection pooling for production
            try:
                self.engine = create_engine(
                    database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True
                )
                # Test connection immediately
                with self.engine.connect() as conn:
                    pass
            except Exception as e:
                import logging
                logging.getLogger("DatabaseManager").warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite.")
                local_fallback = "sqlite:///C:/Users/prann/.gemini/antigravity/scratch/bms-platform/backend/data/service.db"
                self.database_url = local_fallback
                self.engine = create_engine(
                    local_fallback,
                    connect_args={"check_same_thread": False}
                )
            
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def init_tables(self, base_class=Base):
        """Create all tables registered to the service's models."""
        base_class.metadata.create_all(bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """FastAPI dependency yielding a managed database session."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

# Factory function to instantiate DatabaseManager for any microservice
def create_db_manager(database_url: str) -> DatabaseManager:
    return DatabaseManager(database_url)
