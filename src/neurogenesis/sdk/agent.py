 from __future__ import annotations
 
 from typing import Optional
 
 from neurogenesis.models.events import EventEnvelope
 from neurogenesis.sdk.manifest import AgentManifestSpec
 
 
 class AgentBase:
     def __init__(self, manifest: AgentManifestSpec) -> None:
         self.manifest = manifest
 
     async def handle(self, envelope: EventEnvelope) -> Optional[EventEnvelope]:
         raise NotImplementedError("Agents must implement handle()")
