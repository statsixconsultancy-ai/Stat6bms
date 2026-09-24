import asyncio
import uuid
import os
from datetime import datetime
from typing import Dict, List, Callable, Any, Coroutine, Optional
import httpx
from pydantic import BaseModel, Field

class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_name: str
    payload: Dict[str, Any]
    org_id: str = "org-acroflow-main"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class EventBus:
    """
    Multi-process asynchronous Event Bus.
    Supports:
    1. Local in-process async event dispatching.
    2. Cross-process distributed event relaying via API Gateway webhooks.
    """
    def __init__(self, gateway_url: Optional[str] = None):
        self.gateway_url = gateway_url or os.getenv("BMS_GATEWAY_URL", "http://localhost:8000")
        self._subscribers: Dict[str, List[Callable[[DomainEvent], Coroutine[Any, Any, None]]]] = {}
        self._event_history: List[DomainEvent] = []

    def subscribe(self, event_name: str, handler: Callable[[DomainEvent], Coroutine[Any, Any, None]]):
        """Register an async handler function for a given domain event name."""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(handler)

    async def register_with_gateway(self, service_port: int, event_names: List[str]):
        """Register service webhook with API Gateway to receive cross-process events."""
        webhook_url = f"http://localhost:{service_port}/webhooks/events"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                for event_name in event_names:
                    await client.post(
                        f"{self.gateway_url}/events/subscribe",
                        json={"event_name": event_name, "webhook_url": webhook_url}
                    )
        except Exception:
            # Gateway might not be up yet; will be retried
            pass

    async def publish(
        self,
        event_name: str,
        payload: Dict[str, Any],
        org_id: str = "org-acroflow-main",
        relay_to_gateway: bool = True
    ) -> DomainEvent:
        """
        Publish a domain event:
        1. Dispatches to all local in-process subscribers.
        2. Relays to the API Gateway to broadcast to other microservice processes.
        """
        event = DomainEvent(
            event_name=event_name,
            payload=payload,
            org_id=org_id
        )
        self._event_history.append(event)
        if len(self._event_history) > 1000:
            self._event_history.pop(0)

        # 1. Dispatch locally in-process
        handlers = self._subscribers.get(event_name, [])
        wildcard_handlers = self._subscribers.get("*", [])
        for handler in handlers + wildcard_handlers:
            asyncio.create_task(self._safe_execute(handler, event))

        # 2. Relay cross-process via Gateway if enabled
        if relay_to_gateway and self.gateway_url:
            asyncio.create_task(self._relay_to_gateway(event))

        return event

    async def _safe_execute(self, handler: Callable[[DomainEvent], Coroutine[Any, Any, None]], event: DomainEvent):
        try:
            await handler(event)
        except Exception as e:
            print(f"[EventBus ERROR] Handler {getattr(handler, '__name__', 'anonymous')} failed on event {event.event_name}: {e}")

    async def _relay_to_gateway(self, event: DomainEvent):
        """Send event to Gateway's broadcast hub."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(
                    f"{self.gateway_url}/events/publish",
                    json=event.model_dump(),
                    headers={"X-Internal-Relay": "true"}
                )
        except Exception:
            # If gateway is offline or standalone test, gracefully ignore
            pass

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [e.model_dump() for e in self._event_history[-limit:]]

    def clear(self):
        self._subscribers.clear()
        self._event_history.clear()

event_bus = EventBus()
