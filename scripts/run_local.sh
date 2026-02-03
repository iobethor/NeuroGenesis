#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
ENV_SOURCE="$ENV_FILE"
WARN_COUNT=0

log() {
  printf "[run] %s\n" "$*"
}

warn() {
  WARN_COUNT=$((WARN_COUNT + 1))
  printf "[run][warn] %s\n" "$*" >&2
}

err() {
  printf "[run][error] %s\n" "$*" >&2
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

if [ ! -f "$ENV_FILE" ] && [ -f "$ROOT_DIR/.env.example" ]; then
  cp "$ROOT_DIR/.env.example" "$ENV_FILE"
  log "Created .env from .env.example"
fi

if [ ! -f "$ENV_SOURCE" ]; then
  ENV_SOURCE="$ROOT_DIR/.env.example"
fi

if [ -f "$ENV_SOURCE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_SOURCE"
  set +a
fi

POSTGRES_USER="${POSTGRES_USER:-neuro}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-neuro}"
POSTGRES_DB="${POSTGRES_DB:-neurogenesis}"

SUDO=""
if [ "$(id -u)" -ne 0 ] && have_cmd sudo; then
  SUDO="sudo"
fi

ensure_docker() {
  if ! have_cmd docker; then
    warn "Docker not found. Install Docker or run scripts/setup_ubuntu.sh"
    return 1
  fi
  if docker info >/dev/null 2>&1; then
    return 0
  fi
  if have_cmd systemctl && [ -n "$SUDO" ]; then
    log "Trying to start Docker daemon via systemctl..."
    $SUDO systemctl start docker >/dev/null 2>&1 || true
    sleep 2
  fi
  if ! docker info >/dev/null 2>&1; then
    warn "Docker daemon is not running."
    return 1
  fi
  return 0
}

ensure_compose() {
  if docker compose version >/dev/null 2>&1; then
    COMPOSE=(docker compose)
    return 0
  fi
  if have_cmd docker-compose; then
    COMPOSE=(docker-compose)
    return 0
  fi
  warn "Docker Compose not found. Install the docker compose plugin."
  return 1
}

compose() {
  "${COMPOSE[@]}" "$@"
}

compose_exec() {
  compose exec -T "$@"
}

check_service_running() {
  local service="$1"
  local cid=""
  cid="$(compose ps -q "$service" 2>/dev/null || true)"
  if [ -z "$cid" ]; then
    warn "Service ${service} container not found."
    return 1
  fi
  local status=""
  status="$(docker inspect -f '{{.State.Status}}' "$cid" 2>/dev/null || true)"
  if [ "$status" != "running" ]; then
    warn "Service ${service} status: ${status:-unknown}."
    return 1
  fi
  log "Service ${service} is running."
  return 0
}

wait_for_postgres() {
  local attempts=20
  local delay=2
  local i=0
  for ((i=1; i<=attempts; i++)); do
    if compose_exec postgres pg_isready -U "$POSTGRES_USER" -d postgres >/dev/null 2>&1; then
      return 0
    fi
    sleep "$delay"
  done
  return 1
}

ensure_postgres_db() {
  local exists=""
  exists="$(compose_exec postgres psql -U "$POSTGRES_USER" -d postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'" 2>/dev/null || true)"
  exists="$(printf "%s" "$exists" | tr -d '[:space:]')"
  if [ "$exists" != "1" ]; then
    log "Creating Postgres database: ${POSTGRES_DB}"
    if ! compose_exec postgres psql -U "$POSTGRES_USER" -d postgres -c \
      "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};" >/dev/null 2>&1; then
      warn "Failed to create Postgres database ${POSTGRES_DB}."
      return 1
    fi
  else
    log "Postgres database ${POSTGRES_DB} already exists."
  fi
  return 0
}

apply_schema() {
  local schema_file="$ROOT_DIR/scripts/db/bootstrap.sql"
  if [ ! -f "$schema_file" ]; then
    warn "Schema file not found (${schema_file}); skipping table creation."
    return 1
  fi
  log "Applying schema from ${schema_file}"
  if ! compose_exec postgres psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    < "$schema_file" >/dev/null 2>&1; then
    warn "Schema apply failed. Check SQL file and retry."
    return 1
  fi
  log "Schema applied."
  return 0
}

wait_for_http() {
  local name="$1"
  local url="$2"
  local attempts=15
  local delay=2
  local i=0
  if ! have_cmd curl; then
    warn "curl not found; skipping ${name} health check."
    return 1
  fi
  for ((i=1; i<=attempts; i++)); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      log "${name} is reachable."
      return 0
    fi
    sleep "$delay"
  done
  warn "${name} not reachable at ${url}."
  return 1
}

if ! ensure_docker || ! ensure_compose; then
  err "Cannot start stack without Docker + Compose."
  exit 1
fi

log "Starting stack via ${COMPOSE[*]}..."
if ! compose up -d --build; then
  warn "Compose up failed. Continuing with checks."
fi

check_service_running postgres || true
check_service_running redis || true
check_service_running qdrant || true
check_service_running api || true
check_service_running console || true

if wait_for_postgres; then
  ensure_postgres_db || true
  apply_schema || true
else
  warn "Postgres is not ready; skipping DB bootstrap."
fi

if compose_exec redis redis-cli ping >/dev/null 2>&1; then
  log "Redis is reachable."
else
  warn "Redis ping failed."
fi

wait_for_http "Qdrant" "http://localhost:6333/collections" || true
wait_for_http "API" "http://localhost:6800/health" || true
wait_for_http "Console" "http://localhost:6300" || true

log "API: http://localhost:6800/health"
log "Console: http://localhost:6300"

if [ "$WARN_COUNT" -gt 0 ]; then
  warn "Completed with ${WARN_COUNT} warning(s)."
fi
