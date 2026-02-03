 from __future__ import annotations
 
 from typing import Any, Dict, Optional
 from uuid import uuid4
 
 from fastapi import APIRouter, Request
 from pydantic import BaseModel, Field
 
 from neurogenesis.models.events import EventEnvelope
 
 router = APIRouter(prefix="/v1/events", tags=["events"])
 
 
 class EventInput(BaseModel):
     event_type: str
     capability: str
     payload: Dict[str, Any] = Field(default_factory=dict)
     metadata: Dict[str, Any] = Field(default_factory=dict)
     trace_id: Optional[str] = None
     budget_ms: Optional[int] = None
     timeout_ms: Optional[int] = None
 
 
 @router.post("")
 async def publish_event(request: Request, body: EventInput) -> dict:
     settings = request.app.state.settings
     envelope = EventEnvelope(
         event_type=body.event_type,
         capability=body.capability,
         payload=body.payload,
         metadata=body.metadata,
         trace_id=body.trace_id or str(uuid4()),
         budget_ms=body.budget_ms or settings.budget_default_ms,
         timeout_ms=body.timeout_ms or settings.timeout_default_ms,
     )
     await request.app.state.event_bus.publish(envelope)
     return {"status": "queued", "event_id": envelope.event_id, "trace_id": envelope.trace_id}
 
 
 @router.get("/traces/{trace_id}")
 async def get_trace(request: Request, trace_id: str) -> dict:
     history = request.app.state.trace_hub.history(trace_id)
     return {
         "trace_id": trace_id,
         "events": [event.__dict__ for event in history],
     }
