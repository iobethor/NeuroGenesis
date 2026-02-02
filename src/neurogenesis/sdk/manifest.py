 from __future__ import annotations
 
 from dataclasses import dataclass, field
 from typing import Any, Dict, List
 
 
 @dataclass
 class AgentManifestSpec:
     agent_id: str
     name: str
     version: str
     capabilities: List[str]
     heartbeat_interval_s: int = 10
     enabled: bool = True
     metadata: Dict[str, Any] = field(default_factory=dict)
