 # Roadmap
 
 ## V0 foundation
 
 - Event envelope with trace_id and budget routing.
 - Agent registry + heartbeats + enable/disable.
 - LLM gateway with streaming adapters.
 - SSE/WS streaming + builder console base UI.
 - Observability hooks (OTel, Prometheus, JSON logs).
 - Resilience primitives + incident log.
 
 ## Next iterations
 
 - Postgres persistence for registry/config/incident log.
 - Timescale metrics ingestion + dashboards.
 - Qdrant memory indexing and retrieval pipelines.
 - External LLM adapters + warm pool service.
 - Policy engine for budgets, routing, and safe mode.
