#!/usr/bin/env bash
#
# NeuroGenesis — Остановка всех сервисов
#

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

GREEN='\033[0;32m'
NC='\033[0m'

log() {
  printf "${GREEN}[NeuroGenesis]${NC} %s\n" "$*"
}

cd "$ROOT_DIR"

log "Останавливаем сервисы..."
docker compose down "$@"
log "Сервисы остановлены."
