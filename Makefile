.PHONY: help setup run clean test docker-build docker-run docker-stop install

help:
	@echo "NeuroGenesis - Available commands:"
	@echo ""
	@echo "  make setup        - Setup project environment"
	@echo "  make run          - Run the project"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run in Docker"
	@echo "  make docker-stop  - Stop Docker containers"
	@echo ""

setup:
	@./setup.sh

run:
	@./run.sh

install:
	@if [ ! -d "venv" ]; then python3 -m venv venv; fi
	@. venv/bin/activate && pip install -r requirements.txt

test:
	@. venv/bin/activate && pytest tests/ -v

clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	@echo "✓ Cleanup complete"

docker-build:
	@docker-compose build

docker-run:
	@./docker-run.sh

docker-stop:
	@docker-compose down
