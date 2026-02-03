 from __future__ import annotations
 
 from datetime import datetime
 from typing import Dict, List
 
 from neurogenesis.models.agents import AgentManifest, AgentStatus
 
 
 class AgentRegistry:
     def __init__(self) -> None:
         self._manifests: Dict[str, AgentManifest] = {}
         self._statuses: Dict[str, AgentStatus] = {}
 
     def register(self, manifest: AgentManifest) -> None:
         self._manifests[manifest.agent_id] = manifest
         self._statuses[manifest.agent_id] = AgentStatus(
             agent_id=manifest.agent_id,
             last_heartbeat=datetime.utcnow(),
             enabled=manifest.enabled,
             healthy=True,
         )
 
     def heartbeat(self, agent_id: str) -> None:
         status = self._statuses.get(agent_id)
         if status:
             status.last_heartbeat = datetime.utcnow()
             status.healthy = True
 
     def set_enabled(self, agent_id: str, enabled: bool) -> None:
         if agent_id in self._manifests:
             self._manifests[agent_id].enabled = enabled
         if agent_id in self._statuses:
             self._statuses[agent_id].enabled = enabled
 
     def list_manifests(self) -> List[AgentManifest]:
         return list(self._manifests.values())
 
     def list_statuses(self) -> List[AgentStatus]:
         return list(self._statuses.values())
