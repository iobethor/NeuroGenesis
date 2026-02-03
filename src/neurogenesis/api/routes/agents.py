 from __future__ import annotations
 
 from fastapi import APIRouter, Request
 
 from neurogenesis.models.agents import AgentManifest
 
 router = APIRouter(prefix="/v1/agents", tags=["agents"])
 
 
 @router.post("/register")
 async def register_agent(request: Request, manifest: AgentManifest) -> dict:
     request.app.state.registry.register(manifest)
     return {"status": "registered", "agent_id": manifest.agent_id}
 
 
 @router.post("/{agent_id}/heartbeat")
 async def heartbeat(request: Request, agent_id: str) -> dict:
     request.app.state.registry.heartbeat(agent_id)
     return {"status": "ok", "agent_id": agent_id}
 
 
 @router.post("/{agent_id}/enable")
 async def enable_agent(request: Request, agent_id: str) -> dict:
     request.app.state.registry.set_enabled(agent_id, True)
     return {"status": "enabled", "agent_id": agent_id}
 
 
 @router.post("/{agent_id}/disable")
 async def disable_agent(request: Request, agent_id: str) -> dict:
     request.app.state.registry.set_enabled(agent_id, False)
     return {"status": "disabled", "agent_id": agent_id}
 
 
 @router.get("")
 async def list_agents(request: Request) -> dict:
     return {
         "manifests": [item.model_dump() for item in request.app.state.registry.list_manifests()],
         "statuses": [item.model_dump() for item in request.app.state.registry.list_statuses()],
     }
