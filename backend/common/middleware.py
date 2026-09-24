import time
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Ensures every inbound request has an X-Correlation-Id for cross-microservice
    tracing and measures execution duration in X-Process-Time-Ms.
    """
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = (time.time() - start_time) * 1000.0
        
        response.headers["X-Correlation-Id"] = correlation_id
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        return response

def setup_microservice_middleware(app: FastAPI, service_name: str, cors_origins=None):
    """Utility to attach standard cross-cutting middleware to any microservice."""
    if cors_origins is None:
        cors_origins = ["*"]
        
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(CorrelationIdMiddleware)
