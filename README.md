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

Самый простой способ (создаст `.env` и поднимет контейнеры):

```bash
bash scripts/run_local.sh
```

или вручную:

```bash
docker compose up -d --build
```

Скрипт `run_local.sh` дополнительно:
- проверяет Docker/Compose и доступность сервисов;
- ждёт Postgres, создаёт базу при необходимости;
- применяет `scripts/db/bootstrap.sql` для создания таблиц (если файл есть).

API: http://localhost:8000/health  
Console: http://localhost:3000

## Установка на Ubuntu (сервер)

Если вы не работали с Docker, используйте скрипт подготовки:

```bash
bash scripts/setup_ubuntu.sh
```

Что делает скрипт:
- ставит нужный софт (Docker Engine + Compose plugin, curl, git, jq);
- копирует `.env.example` в `.env`, если файла нет;
- проверяет свободные порты (8000/3000/5432/6379/6333);
- если Postgres установлен локально — создаёт роль и БД.

Опции:
- `--skip-docker` — пропустить установку Docker.
- `--skip-postgres` — пропустить создание БД.

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
