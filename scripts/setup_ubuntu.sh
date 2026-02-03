#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
  ENV_FILE="$ROOT_DIR/.env.example"
fi

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

POSTGRES_USER="${POSTGRES_USER:-neuro}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-neuro}"
POSTGRES_DB="${POSTGRES_DB:-neurogenesis}"

SKIP_DOCKER=false
SKIP_POSTGRES=false

for arg in "$@"; do
  case "$arg" in
    --skip-docker) SKIP_DOCKER=true ;;
    --skip-postgres) SKIP_POSTGRES=true ;;
    *) ;;
  esac
done

log() {
  printf "[setup] %s\n" "$*"
}

warn() {
  printf "[setup][warn] %s\n" "$*" >&2
}

require_apt() {
  if ! command -v apt-get >/dev/null 2>&1; then
    warn "This script expects apt-get (Ubuntu/Debian)."
    exit 1
  fi
}

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  else
    warn "sudo not found; run as root."
    exit 1
  fi
fi

if [ -f /etc/os-release ]; then
  # shellcheck disable=SC1091
  . /etc/os-release
  if [ "${ID:-}" != "ubuntu" ]; then
    warn "Detected ID=${ID:-unknown}; script is tuned for Ubuntu."
  fi
fi

require_apt

$SUDO apt-get update -y
$SUDO apt-get install -y curl ca-certificates gnupg lsb-release git jq iproute2

if [ ! -f "$ROOT_DIR/.env" ] && [ -f "$ROOT_DIR/.env.example" ]; then
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  log "Created .env from .env.example"
fi

install_docker() {
  log "Installing Docker Engine and Compose plugin..."
  $SUDO install -m 0755 -d /etc/apt/keyrings
  if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    $SUDO chmod a+r /etc/apt/keyrings/docker.gpg
  fi
  local codename=""
  if [ -f /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    codename="${VERSION_CODENAME:-}"
  fi
  if [ -z "$codename" ]; then
    codename="$(lsb_release -cs)"
  fi
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${codename} stable" | $SUDO tee /etc/apt/sources.list.d/docker.list > /dev/null
  $SUDO apt-get update -y
  $SUDO apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  if command -v systemctl >/dev/null 2>&1; then
    $SUDO systemctl enable --now docker || true
  fi
  if [ "$(id -u)" -ne 0 ]; then
    if ! groups "$USER" | awk '{for (i=1;i<=NF;i++) if ($i=="docker") found=1} END {exit found?0:1}'; then
      $SUDO usermod -aG docker "$USER" || true
      warn "Added $USER to docker group. Re-login required."
    fi
  fi
}

if [ "$SKIP_DOCKER" = false ]; then
  if ! command -v docker >/dev/null 2>&1; then
    install_docker
  else
    log "Docker already installed."
  fi
  if ! docker compose version >/dev/null 2>&1; then
    warn "Docker Compose plugin is missing. Re-run install or install docker-compose-plugin."
  fi
else
  log "Skipping Docker setup."
fi

check_port() {
  local port="$1"
  if ss -tulnH | awk -v port=":$port" '$5 ~ port"$" {found=1} END {exit found?0:1}'; then
    warn "Port $port is in use."
  else
    log "Port $port is free."
  fi
}

log "Checking required ports..."
check_port 6800
check_port 6300
check_port 6543
check_port 6379
check_port 6333

if [ "$SKIP_POSTGRES" = false ] && command -v psql >/dev/null 2>&1; then
  if $SUDO -u postgres psql -tAc "SELECT 1" >/dev/null 2>&1; then
    if ! $SUDO -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'" | grep -q 1; then
      log "Creating Postgres role: ${POSTGRES_USER}"
      $SUDO -u postgres psql -c "CREATE ROLE ${POSTGRES_USER} WITH LOGIN PASSWORD '${POSTGRES_PASSWORD}';"
    else
      log "Postgres role ${POSTGRES_USER} already exists."
    fi
    if ! $SUDO -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'" | grep -q 1; then
      log "Creating Postgres database: ${POSTGRES_DB}"
      $SUDO -u postgres psql -c "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};"
    else
      log "Postgres database ${POSTGRES_DB} already exists."
    fi
  else
    warn "psql found, but cannot connect as postgres. Skipping DB bootstrap."
  fi
else
  log "Skipping Postgres bootstrap."
fi

log "Setup complete."
log "Next: docker compose up -d --build"
