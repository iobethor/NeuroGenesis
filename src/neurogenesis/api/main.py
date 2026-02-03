 from __future__ import annotations
 
 import asyncio
 from typing import Optional
 
 from fastapi import FastAPI
 
 from neurogenesis.core.config import load_settings
 from neurogenesis.core.event_bus import EventBus
 from neurogenesis.core.incidents import IncidentLog
 from neurogenesis.core.llm_gateway import LLMGateway
 from neurogenesis.core.observability import configure_observability, get_prometheus_app
 from neurogenesis.core.registry import AgentRegistry
 from neurogenesis.core.trace_hub import TraceHub
 from neurogenesis.models.events import EventEnvelope
 
 from neurogenesis.api.routes import agents, events, health, llm, stream, ws
 
 
 def create_app() -> FastAPI:
     settings = load_settings()
     app = FastAPI(title="NeuroGenesis API", version="0.1.0")
     configure_observability(app, settings.log_level)
 
     trace_hub = TraceHub()
     incident_log = IncidentLog()
     registry = AgentRegistry()
     event_bus = EventBus(settings, trace_hub, incident_log)
     llm_gateway = LLMGateway()
 
     app.state.settings = settings
     app.state.trace_hub = trace_hub
     app.state.incident_log = incident_log
     app.state.registry = registry
     app.state.event_bus = event_bus
     app.state.llm_gateway = llm_gateway
 
     app.include_router(health.router)
     app.include_router(events.router)
     app.include_router(stream.router)
     app.include_router(agents.router)
     app.include_router(llm.router)
     app.include_router(ws.router)
 
     metrics_app = get_prometheus_app()
     if metrics_app:
         app.mount("/metrics", metrics_app)
 
     @app.on_event("startup")
     async def _startup() -> None:
         await event_bus.start()
 
     @app.on_event("shutdown")
     async def _shutdown() -> None:
         await event_bus.stop()
 
     async def echo_handler(envelope: EventEnvelope) -> Optional[EventEnvelope]:
         await asyncio.sleep(0.01)
         return EventEnvelope(
             event_type="echo",
             capability=envelope.capability,
             trace_id=envelope.trace_id,
             source="core",
             payload=envelope.payload,
             metadata={"echo": True},
         )
 
     event_bus.register("echo", echo_handler)
     return app
 
 
 app = create_app()
