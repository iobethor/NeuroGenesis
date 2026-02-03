 from __future__ import annotations
 
 from typing import Any, Dict, Optional
 
 import httpx
 
 from neurogenesis.sdk.manifest import AgentManifestSpec
 
 
 class AgentClient:
     def __init__(self, base_url: str, manifest: AgentManifestSpec) -> None:
         self.base_url = base_url.rstrip("/")
         self.manifest = manifest
 
     async def register(self) -> Dict[str, Any]:
         async with httpx.AsyncClient() as client:
             response = await client.post(
                 f"{self.base_url}/v1/agents/register",
                 json={
                     "agent_id": self.manifest.agent_id,
                     "name": self.manifest.name,
                     "version": self.manifest.version,
                     "capabilities": self.manifest.capabilities,
                     "heartbeat_interval_s": self.manifest.heartbeat_interval_s,
                     "enabled": self.manifest.enabled,
                     "metadata": self.manifest.metadata,
                 },
                 timeout=10,
             )
             response.raise_for_status()
             return response.json()
 
     async def heartbeat(self) -> Dict[str, Any]:
         async with httpx.AsyncClient() as client:
             response = await client.post(
                 f"{self.base_url}/v1/agents/{self.manifest.agent_id}/heartbeat",
                 timeout=10,
             )
             response.raise_for_status()
             return response.json()
 
     async def send_event(
         self,
         event_type: str,
         capability: str,
         payload: Optional[Dict[str, Any]] = None,
         trace_id: Optional[str] = None,
     ) -> Dict[str, Any]:
         async with httpx.AsyncClient() as client:
             response = await client.post(
                 f"{self.base_url}/v1/events",
                 json={
                     "event_type": event_type,
                     "capability": capability,
                     "payload": payload or {},
                     "trace_id": trace_id,
                 },
                 timeout=10,
             )
             response.raise_for_status()
             return response.json()
