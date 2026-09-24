"""
BMS Common Shared Library
Provides foundation classes and utilities for all BMS microservices.
"""
from common.config import ServiceConfig, get_service_config
from common.models import Base, TenantModel, generate_uuid
from common.database import DatabaseManager, create_db_manager
from common.security import (
    UserContext,
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    get_user_context
)
from common.event_bus import DomainEvent, EventBus, event_bus
from common.middleware import CorrelationIdMiddleware, setup_microservice_middleware

__all__ = [
    "ServiceConfig",
    "get_service_config",
    "Base",
    "TenantModel",
    "generate_uuid",
    "DatabaseManager",
    "create_db_manager",
    "UserContext",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "get_user_context",
    "DomainEvent",
    "EventBus",
    "event_bus",
    "CorrelationIdMiddleware",
    "setup_microservice_middleware"
]
