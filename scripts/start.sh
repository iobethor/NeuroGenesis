#!/usr/bin/env bash
#
# NeuroGenesis — Единый скрипт запуска
# Устанавливает зависимости (если нужно) и запускает все сервисы
#

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

# --- Цвета и вывод ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log() {
  printf "${GREEN}[NeuroGenesis]${NC} %s\n" "$*"
}

warn() {
  printf "${YELLOW}[NeuroGenesis][warn]${NC} %s\n" "$*" >&2
}

error() {
  printf "${RED}[NeuroGenesis][error]${NC} %s\n" "$*" >&2
}

info() {
  printf "${CYAN}[NeuroGenesis]${NC} %s\n" "$*"
}

header() {
  echo ""
  printf "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
  printf "${BLUE}  %s${NC}\n" "$*"
  printf "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
  echo ""
}

# --- Опции ---
FORCE_REBUILD=false
SKIP_SETUP=false
DETACH=true
SHOW_LOGS=false

usage() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Запускает NeuroGenesis (устанавливает зависимости при первом запуске)"
  echo ""
  echo "Options:"
  echo "  --rebuild      Пересобрать все контейнеры"
  echo "  --skip-setup   Пропустить проверку/установку Docker"
  echo "  --logs         Показать логи после запуска (интерактивно)"
  echo "  --foreground   Запустить в режиме переднего плана (без -d)"
  echo "  -h, --help     Показать эту справку"
  echo ""
  echo "Examples:"
  echo "  $0                  # Обычный запуск"
  echo "  $0 --rebuild        # Пересобрать контейнеры"
  echo "  $0 --logs           # Запустить и показать логи"
}

for arg in "$@"; do
  case "$arg" in
    --rebuild) FORCE_REBUILD=true ;;
    --skip-setup) SKIP_SETUP=true ;;
    --logs) SHOW_LOGS=true ;;
    --foreground) DETACH=false ;;
    -h|--help) usage; exit 0 ;;
    *) warn "Неизвестная опция: $arg"; usage; exit 1 ;;
  esac
done

# --- Определение sudo ---
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  fi
fi

# --- Проверка ОС ---
detect_os() {
  if [ -f /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    echo "${ID:-unknown}"
  elif [ "$(uname)" = "Darwin" ]; then
    echo "macos"
  else
    echo "unknown"
  fi
}

OS_ID="$(detect_os)"

# --- Установка Docker ---
install_docker_ubuntu() {
  log "Устанавливаем Docker Engine и Compose plugin..."
  $SUDO apt-get update -y
  $SUDO apt-get install -y curl ca-certificates gnupg lsb-release
  
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
    codename="$(lsb_release -cs 2>/dev/null || echo 'jammy')"
  fi
  
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${codename} stable" | $SUDO tee /etc/apt/sources.list.d/docker.list > /dev/null
  $SUDO apt-get update -y
  $SUDO apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  
  if command -v systemctl >/dev/null 2>&1; then
    $SUDO systemctl enable --now docker || true
  fi
  
  if [ "$(id -u)" -ne 0 ]; then
    if ! groups "$USER" 2>/dev/null | grep -q docker; then
      $SUDO usermod -aG docker "$USER" || true
      warn "Добавлен в группу docker. Требуется перелогин или 'newgrp docker'"
    fi
  fi
}

install_docker_debian() {
  install_docker_ubuntu  # Процесс очень похож
}

install_docker_macos() {
  if command -v brew >/dev/null 2>&1; then
    log "Устанавливаем Docker через Homebrew..."
    brew install --cask docker
    warn "Запустите Docker Desktop вручную после установки"
  else
    error "Homebrew не найден. Установите Docker Desktop вручную:"
    error "https://docs.docker.com/desktop/install/mac-install/"
    exit 1
  fi
}

ensure_docker() {
  if [ "$SKIP_SETUP" = true ]; then
    return 0
  fi
  
  if command -v docker >/dev/null 2>&1; then
    log "Docker уже установлен."
  else
    header "Установка Docker"
    case "$OS_ID" in
      ubuntu) install_docker_ubuntu ;;
      debian) install_docker_debian ;;
      macos)  install_docker_macos ;;
      *)
        error "Автоустановка Docker не поддерживается для $OS_ID"
        error "Установите Docker вручную: https://docs.docker.com/engine/install/"
        exit 1
        ;;
    esac
  fi
  
  # Проверяем docker compose
  if ! docker compose version >/dev/null 2>&1; then
    error "Docker Compose plugin не найден."
    error "Установите: sudo apt-get install docker-compose-plugin"
    exit 1
  fi
  
  # Проверяем, что Docker daemon работает
  if ! docker info >/dev/null 2>&1; then
    if [ "$OS_ID" = "macos" ]; then
      error "Docker daemon не запущен. Запустите Docker Desktop."
    else
      warn "Docker daemon не запущен. Пытаемся запустить..."
      $SUDO systemctl start docker 2>/dev/null || true
      sleep 2
      if ! docker info >/dev/null 2>&1; then
        error "Не удалось запустить Docker daemon."
        error "Попробуйте: sudo systemctl start docker"
        exit 1
      fi
    fi
  fi
}

# --- Подготовка окружения ---
setup_env() {
  header "Подготовка окружения"
  
  if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ROOT_DIR/.env.example" ]; then
      cp "$ROOT_DIR/.env.example" "$ENV_FILE"
      log "Создан .env из .env.example"
    else
      warn ".env.example не найден, создаём минимальный .env"
      cat > "$ENV_FILE" << 'EOF'
NG_LOG_LEVEL=INFO
NG_SAFE_MODE=false
POSTGRES_USER=neuro
POSTGRES_PASSWORD=neuro
POSTGRES_DB=neurogenesis
EOF
    fi
  else
    log ".env уже существует"
  fi
}

# --- Проверка портов ---
check_ports() {
  local ports=(8000 3000 5432 6379 6333)
  local busy=()
  
  for port in "${ports[@]}"; do
    if command -v ss >/dev/null 2>&1; then
      if ss -tulnH 2>/dev/null | grep -q ":${port} "; then
        busy+=("$port")
      fi
    elif command -v lsof >/dev/null 2>&1; then
      if lsof -i ":${port}" -sTCP:LISTEN >/dev/null 2>&1; then
        busy+=("$port")
      fi
    fi
  done
  
  if [ ${#busy[@]} -gt 0 ]; then
    warn "Занятые порты: ${busy[*]}"
    warn "Остановите процессы или измените порты в docker-compose.yml"
  else
    log "Все порты свободны (8000, 3000, 5432, 6379, 6333)"
  fi
}

# --- Запуск контейнеров ---
start_containers() {
  header "Запуск NeuroGenesis"
  
  cd "$ROOT_DIR"
  
  local compose_args=()
  
  if [ "$FORCE_REBUILD" = true ]; then
    log "Пересборка контейнеров..."
    compose_args+=(--build)
  fi
  
  if [ "$DETACH" = true ]; then
    compose_args+=(-d)
  fi
  
  log "Запускаем docker compose up ${compose_args[*]}..."
  docker compose up "${compose_args[@]}"
}

# --- Проверка здоровья ---
wait_for_health() {
  if [ "$DETACH" = false ]; then
    return 0
  fi
  
  header "Проверка запуска"
  
  log "Ожидаем готовности сервисов..."
  
  local max_attempts=30
  local attempt=0
  
  while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q "200"; then
      log "API готов! ✓"
      break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
      warn "API не ответил за $max_attempts секунд"
      warn "Проверьте логи: docker compose logs api"
    fi
    
    sleep 1
  done
}

# --- Показать статус ---
show_status() {
  if [ "$DETACH" = false ]; then
    return 0
  fi
  
  header "Статус сервисов"
  
  cd "$ROOT_DIR"
  docker compose ps
  
  echo ""
  printf "${GREEN}════════════════════════════════════════════════════════${NC}\n"
  printf "${GREEN}  NeuroGenesis запущен!${NC}\n"
  printf "${GREEN}════════════════════════════════════════════════════════${NC}\n"
  echo ""
  info "📡 API:     http://localhost:8000"
  info "📡 Health:  http://localhost:8000/health"
  info "🖥️  Console: http://localhost:3000"
  info "🐘 Postgres: localhost:5432 (neuro/neuro)"
  info "📦 Redis:   localhost:6379"
  info "🔍 Qdrant:  localhost:6333"
  echo ""
  info "Команды:"
  info "  Логи:     docker compose logs -f"
  info "  Остановка: docker compose down"
  info "  Рестарт:  $0 --rebuild"
  echo ""
}

# --- Показать логи ---
show_logs() {
  if [ "$SHOW_LOGS" = true ] && [ "$DETACH" = true ]; then
    header "Логи (Ctrl+C для выхода)"
    cd "$ROOT_DIR"
    docker compose logs -f
  fi
}

# --- Главная функция ---
main() {
  header "NeuroGenesis Startup"
  
  ensure_docker
  setup_env
  check_ports
  start_containers
  wait_for_health
  show_status
  show_logs
}

main
