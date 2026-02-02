 from __future__ import annotations
 
 from datetime import datetime
 from typing import Any, Dict, Optional
 from uuid import uuid4
 
 from pydantic import BaseModel, Field
 
 
 class Incident(BaseModel):
     incident_id: str = Field(default_factory=lambda: str(uuid4()))
     trace_id: Optional[str] = None
     severity: str = "error"
     message: str
     context: Dict[str, Any] = Field(default_factory=dict)
     created_at: datetime = Field(default_factory=datetime.utcnow)
     status: str = "open"
