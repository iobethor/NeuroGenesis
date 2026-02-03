.PHONY: start stop restart logs lint test run setup rebuild status health

# ==================== Запуск ====================

# Запустить все сервисы (автоустановка зависимостей при первом запуске)
start:
	@bash scripts/start.sh

# Остановить все сервисы
stop:
	docker compose down

# Перезапустить с пересборкой
restart:
	docker compose down
	@bash scripts/start.sh --rebuild

# Пересобрать контейнеры
rebuild:
	@bash scripts/start.sh --rebuild

# Показать логи
logs:
	docker compose logs -f

# Показать логи API
logs-api:
	docker compose logs -f api

# Статус контейнеров
status:
	docker compose ps

# Проверить здоровье API
health:
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "API не отвечает"

# ==================== Разработка ====================

# Только настройка окружения (без запуска)
setup:
	@bash scripts/setup_ubuntu.sh

# Запустить API локально (без Docker)
run:
	uvicorn neurogenesis.api.main:app --host 0.0.0.0 --port 8000 --reload

# Установить зависимости для локальной разработки
install:
	pip install -e ".[dev,observability]"

# ==================== Тестирование ====================

# Запустить тесты
test:
	pytest -v

# Запустить smoke-тест
smoke:
	@curl -sf http://localhost:8000/health && echo "✓ API healthy" || echo "✗ API not responding"

# ==================== Качество кода ====================

# Проверка линтером
lint:
	ruff check .
	mypy src

# Форматирование кода
format:
	ruff check --fix .
	ruff format .

# ==================== Утилиты ====================

# Очистить Docker (контейнеры, образы, volumes)
clean:
	docker compose down -v --rmi local

# Показать справку
help:
	@echo ""
	@echo "NeuroGenesis - Доступные команды:"
	@echo ""
	@echo "  make start      - Запустить все сервисы (+ автоустановка Docker)"
	@echo "  make stop       - Остановить все сервисы"
	@echo "  make restart    - Перезапустить с пересборкой"
	@echo "  make rebuild    - Пересобрать контейнеры"
	@echo "  make logs       - Показать логи всех сервисов"
	@echo "  make status     - Статус контейнеров"
	@echo "  make health     - Проверить здоровье API"
	@echo ""
	@echo "  make run        - Запустить API локально (без Docker)"
	@echo "  make install    - Установить Python-зависимости"
	@echo "  make test       - Запустить тесты"
	@echo "  make lint       - Проверка линтером"
	@echo "  make format     - Форматирование кода"
	@echo ""
	@echo "  make clean      - Удалить контейнеры и образы"
	@echo "  make help       - Эта справка"
	@echo ""
