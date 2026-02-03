 # Architecture
 
 ## Core principles
 
 - Event-driven routing by capability with strict budgets and fallbacks.
 - Agents are plugins with manifests + heartbeats.
 - Streaming-first APIs (SSE/WS) for tokens and trace events.
 - Observability built-in (traces, metrics, JSON logs).
 - Resilience over failure: retry/backoff, circuit breakers, incident log.
 
 ## Components
 
 - **API Core (FastAPI)**: event router, agent registry, LLM gateway, SSE/WS.
 - **Builder Console (Next.js)**: live traces, module control, budgets, incidents.
 - **CLI**: admin automation (up/down, migrate, seed, smoke, export traces).
 - **SDK**: agent API (manifest, client, handler base).
 
 ## Data stores
 
 - Postgres + TimescaleDB: configs, registry, audit, incident log, metrics.
 - Qdrant: semantic memory layer.
 - Redis: cache, transient state, rate limiting.
