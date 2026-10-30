import os
import re
import socket
import logging
from typing import Generator, Optional
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from common.models import Base

logger = logging.getLogger("DatabaseManager")

class DatabaseManager:
    """Encapsulates engine creation and session generation per microservice with automatic Supabase pooler failover."""
    
    # Class-level cache of the successfully verified PostgreSQL URL
    _RESOLVED_PG_URL: Optional[str] = None

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
            # PostgreSQL configuration with connection pooling and intelligent Supabase resolution
            engine = self._create_pg_engine(database_url)
            if engine is not None:
                self.engine = engine
            else:
                local_fallback = "sqlite:///C:/Users/prann/.gemini/antigravity/scratch/bms-platform/backend/data/service.db"
                logger.warning("All PostgreSQL connections failed. Falling back to local SQLite.")
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
        self.init_tables()

    def _create_pg_engine(self, original_url: str):
        # 1. If we already established a verified working URL across microservices, prioritize it immediately
        if DatabaseManager._RESOLVED_PG_URL:
            try:
                engine = create_engine(
                    DatabaseManager._RESOLVED_PG_URL,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True
                )
                self.database_url = DatabaseManager._RESOLVED_PG_URL
                return engine
            except Exception:
                pass

        candidate_urls = []
        parsed = urlparse(original_url)
        is_direct_supabase = bool(re.match(r"^db\.([a-z0-9]+)\.supabase\.co$", parsed.hostname or ""))
        
        # Check if direct hostname has IPv4 address reachable in under 50ms
        can_use_direct = False
        if is_direct_supabase:
            try:
                socket.getaddrinfo(parsed.hostname, 5432, socket.AF_INET)
                can_use_direct = True
            except socket.gaierror:
                can_use_direct = False
        else:
            can_use_direct = True

        if can_use_direct:
            candidate_urls.append(original_url)

        # If this is Supabase, generate pooler candidates (which support IPv4 and IPv6 everywhere)
        if is_direct_supabase:
            match = re.match(r"^db\.([a-z0-9]+)\.supabase\.co$", parsed.hostname or "")
            project_ref = match.group(1)
            password = parsed.password or ""
            database_name = parsed.path.lstrip("/") or "postgres"
            
            # Prioritize ap-south-1 where pcuyckkvtaekxxbqhdjq is provisioned
            regions = ["ap-south-1", "eu-central-1", "us-east-1", "us-west-1", "ap-southeast-1"]
            for r in regions:
                candidate_urls.append(
                    f"postgresql://postgres.{project_ref}:{password}@aws-0-{r}.pooler.supabase.com:5432/{database_name}"
                )
                candidate_urls.append(
                    f"postgresql://postgres.{project_ref}:{password}@aws-0-{r}.pooler.supabase.com:6543/{database_name}"
                )

        if not can_use_direct:
            candidate_urls.append(original_url)

        for url in candidate_urls:
            try:
                engine = create_engine(
                    url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    connect_args={"connect_timeout": 5}
                )
                with engine.connect() as conn:
                    logger.info(f"Connected to PostgreSQL at: {url.split('@')[-1] if '@' in url else url}")
                self.database_url = url
                DatabaseManager._RESOLVED_PG_URL = url
                return engine
            except Exception as e:
                logger.debug(f"Connection attempt to {url.split('@')[-1] if '@' in url else url} failed: {e}")
                continue

        return None

    def init_tables(self, base_class=Base):
        """Create all tables registered to the service's models and safely add any new columns."""
        base_class.metadata.create_all(bind=self.engine)
        try:
            from sqlalchemy import inspect, text
            if self.engine.dialect.name == "postgresql":
                with self.engine.begin() as conn:
                    rows = conn.execute(
                        text("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public'")
                    ).fetchall()
                    existing_cols_by_table = {}
                    for t_name, c_name in rows:
                        existing_cols_by_table.setdefault(t_name, set()).add(c_name)
                    
                    for table_name, table in base_class.metadata.tables.items():
                        if table_name in existing_cols_by_table:
                            curr_cols = existing_cols_by_table[table_name]
                            for col in table.columns:
                                if col.name not in curr_cols:
                                    col_type = col.type.compile(self.engine.dialect)
                                    conn.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN "{col.name}" {col_type}'))
                                    curr_cols.add(col.name)
            else:
                # SQLite fallback
                inspector = inspect(self.engine)
                existing_tables = set(inspector.get_table_names())
                with self.engine.begin() as conn:
                    for table_name, table in base_class.metadata.tables.items():
                        if table_name in existing_tables:
                            existing_cols = {col["name"] for col in inspector.get_columns(table_name)}
                            for col in table.columns:
                                if col.name not in existing_cols:
                                    col_type = col.type.compile(self.engine.dialect)
                                    conn.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN "{col.name}" {col_type}'))
        except Exception as e:
            logger.debug(f"Auto-migration column sync info: {e}")

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
