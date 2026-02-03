#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

log() {
  printf "[run] %s\n" "$*"
}

err() {
  printf "[run][error] %s\n" "$*" >&2
}

if [ ! -f "$ENV_FILE" ] && [ -f "$ROOT_DIR/.env.example" ]; then
  cp "$ROOT_DIR/.env.example" "$ENV_FILE"
  log "Created .env from .env.example"
fi

if ! command -v docker >/dev/null 2>&1; then
  err "Docker not found. Install Docker or run scripts/setup_ubuntu.sh"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  err "Docker daemon is not running. Start Docker and retry."
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  err "Docker Compose not found. Install the docker compose plugin."
  exit 1
fi

log "Starting stack via ${COMPOSE[*]}..."
"${COMPOSE[@]}" up -d --build

log "API: http://localhost:8000/health"
log "Console: http://localhost:3000"
