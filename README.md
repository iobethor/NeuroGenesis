# NeuroGenesis

Проект: «растущий разум» с активной семантической памятью.

## Что это

NeuroGenesis — event-driven core с агентами, стримингом и наблюдаемостью:

- **Web-сервис**: ядро событий, routing по capabilities, бюджеты и fallback.
- **Builder Console (Web)**: live traces, управление агентами и конфигами.
- **CLI**: админ-операции (up/down/migrate/seed/smoke/export traces).
- **SDK**: подключение агентов как «розетка 220».
- **Telegram**: коннектор поверх API (не отдельный продукт).

## 🚀 Быстрый старт (одна команда)

**Запуск на любой системе (Ubuntu/Debian/macOS):**

```bash
make start
```

или напрямую:

```bash
bash scripts/start.sh
```

Скрипт автоматически:
- Установит Docker и Docker Compose (если не установлены)
- Создаст `.env` из примера (если нет)
- Проверит свободные порты
- Соберёт и запустит все контейнеры
- Покажет статус и ссылки

После запуска:
- **API**: http://localhost:8000
- **Health**: http://localhost:8000/health
- **Console**: http://localhost:3000

## 📋 Основные команды

```bash
make start     # Запустить всё (+ автоустановка Docker)
make stop      # Остановить все сервисы
make restart   # Перезапустить с пересборкой
make logs      # Показать логи
make status    # Статус контейнеров
make health    # Проверить API
make help      # Справка по всем командам
```

## ⚙️ Опции запуска

```bash
bash scripts/start.sh                 # Обычный запуск
bash scripts/start.sh --rebuild       # Пересобрать контейнеры
bash scripts/start.sh --logs          # Запустить и показать логи
bash scripts/start.sh --skip-setup    # Пропустить установку Docker
bash scripts/start.sh --foreground    # Без detach (логи в консоль)
```

## 🛠️ Ручная установка (если нужна)

Если предпочитаете ручную установку Docker:

```bash
# 1. Подготовка системы (опционально)
bash scripts/setup_ubuntu.sh

# 2. Запуск
docker compose up -d --build
```

## 📡 Основные эндпоинты API

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/v1/events` | Публиковать события (EventEnvelope) |
| GET | `/v1/stream/{trace_id}` | SSE стрим событий по trace_id |
| POST | `/v1/llm/stream` | SSE стрим токенов LLM |
| POST | `/v1/agents/register` | Регистрация агента |
| POST | `/v1/agents/{id}/heartbeat` | Heartbeat агента |
| GET | `/v1/events/traces/{trace_id}` | История трейса |

## 🧪 Разработка

```bash
# Установить зависимости локально
make install

# Запустить API без Docker (для отладки)
make run

# Тесты
make test

# Линтер и форматирование
make lint
make format
```

## 📖 Документация

- Архитектура: `docs/architecture.md`
- Roadmap: `docs/ROADMAP.md`

## 🔧 Устранение проблем

**Docker не запускается:**
```bash
# Ubuntu/Debian
sudo systemctl start docker

# macOS
open -a Docker
```

**Порты заняты:**
```bash
# Проверить какие порты заняты
ss -tulnp | grep -E '(8000|3000|5432|6379|6333)'

# Или остановить всё и перезапустить
make clean
make start
```

**Пересборка с нуля:**
```bash
make clean      # Удалить контейнеры и образы
make start      # Запустить заново
```

## 📜 Лицензия

Apache-2.0
