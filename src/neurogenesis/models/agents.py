 from __future__ import annotations
 
 from datetime import datetime
 from typing import Any, Dict, List
 
 from pydantic import BaseModel, Field
 
 
 class AgentManifest(BaseModel):
     agent_id: str
     name: str
     version: str
     capabilities: List[str]
     heartbeat_interval_s: int = 10
     enabled: bool = True
     metadata: Dict[str, Any] = Field(default_factory=dict)
 
 
 class AgentStatus(BaseModel):
     agent_id: str
     last_heartbeat: datetime
     enabled: bool = True
     healthy: bool = True
