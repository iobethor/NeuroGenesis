 from __future__ import annotations
 
 from datetime import datetime
 from typing import Any, Dict
 from uuid import uuid4
 
 from pydantic import BaseModel, Field
 
 
 class EventEnvelope(BaseModel):
     event_id: str = Field(default_factory=lambda: str(uuid4()))
     trace_id: str = Field(default_factory=lambda: str(uuid4()))
     event_type: str
     capability: str
     source: str = "api"
     created_at: datetime = Field(default_factory=datetime.utcnow)
     payload: Dict[str, Any] = Field(default_factory=dict)
     metadata: Dict[str, Any] = Field(default_factory=dict)
     budget_ms: int = 3000
     timeout_ms: int = 1500
     attempt: int = 0
