# NeuroGenesis

Проект: «растущий разум» с активной семантической памятью.

## Что это

NeuroGenesis — event-driven core с агентами, стримингом и наблюдаемостью:

- **Web-сервис**: ядро событий, routing по capabilities, бюджеты и fallback.
- **Builder Console (Web)**: live traces, управление агентами и конфигами.
- **CLI**: админ-операции (up/down/migrate/seed/smoke/export traces).
- **SDK**: подключение агентов как «розетка 220».
- **Telegram**: коннектор поверх API (не отдельный продукт).

## Быстрый старт (локально)

```bash
docker compose up -d --build
```

API: http://localhost:8000/health  
Console: http://localhost:3000

## Основные эндпоинты API

- `POST /v1/events` — публиковать события (EventEnvelope)
- `GET /v1/stream/{trace_id}` — SSE стрим событий по trace_id
- `POST /v1/llm/stream` — SSE стрим токенов LLM
- `POST /v1/agents/register` — регистрация агента
- `POST /v1/agents/{id}/heartbeat` — heartbeat
- `GET /v1/events/traces/{trace_id}` — история трейса

## CLI

```bash
ng up
ng smoke --base-url http://localhost:8000
```

## Архитектура и планы

- Документация: `docs/architecture.md`
- Roadmap: `docs/ROADMAP.md`

## Лицензия

Apache-2.0
