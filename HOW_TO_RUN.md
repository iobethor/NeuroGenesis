# 🚀 Как запустить NeuroGenesis

## Самый простой способ ⭐

```bash
./start.sh
```

**Это всё!** Один скрипт делает всё автоматически.

---

## Что делает start.sh?

```
┌─────────────────────────────────────────┐
│         ./start.sh                      │
│                                         │
│  1. ✓ Проверка Python 3                │
│  2. ✓ Создание venv/                   │
│  3. ✓ Установка зависимостей           │
│  4. ✓ Создание структуры проекта       │
│  5. ✓ Запуск приложения                │
└─────────────────────────────────────────┘
```

---

## Другие способы запуска

### Способ 1: Раздельно

```bash
# Шаг 1: Настройка (один раз)
./setup.sh

# Шаг 2: Запуск (каждый раз)
./run.sh
```

### Способ 2: Make

```bash
# Посмотреть все команды
make help

# Настройка
make setup

# Запуск
make run

# Тесты
make test
```

### Способ 3: Docker

```bash
# Запустить в контейнере
./docker-run.sh

# Или напрямую
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Способ 4: Вручную

```bash
# Активировать окружение
source venv/bin/activate

# Запустить
python3 src/main.py

# Деактивировать (когда закончите)
deactivate
```

---

## Блок-схема выбора метода

```
          Вы хотите запустить NeuroGenesis?
                       │
                       ├─── Самый простой? ──→ ./start.sh
                       │
                       ├─── Уже настроено? ──→ ./run.sh
                       │
                       ├─── Использую Make? ──→ make run
                       │
                       ├─── Нужен Docker? ──→ ./docker-run.sh
                       │
                       └─── Ручной режим? ──→ source venv/bin/activate
                                              python3 src/main.py
```

---

## Визуальное сравнение

| Способ | Команда | Когда использовать |
|--------|---------|-------------------|
| ⭐ **start.sh** | `./start.sh` | Первый запуск или когда нужно всё |
| 🔄 **run.sh** | `./run.sh` | Когда уже настроено |
| 🛠️ **Make** | `make run` | Если любите Make |
| 🐳 **Docker** | `./docker-run.sh` | Изолированное окружение |
| 🔧 **Вручную** | `source venv/bin/activate` | Полный контроль |

---

## Примеры использования

### Пример 1: Первый раз

```bash
git clone https://github.com/iobethor/NeuroGenesis
cd NeuroGenesis
./start.sh
```

### Пример 2: Второй раз

```bash
cd NeuroGenesis
./run.sh
```

### Пример 3: Разработка

```bash
source venv/bin/activate
python3 src/main.py
# Работайте с кодом
pytest tests/
deactivate
```

---

## Проблемы?

### Ошибка: Permission denied

```bash
chmod +x *.sh
```

### Ошибка: Python not found

Ubuntu/Debian:
```bash
sudo apt install python3 python3-pip python3-venv
```

macOS:
```bash
brew install python3
```

### Ошибка при установке зависимостей

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

---

## Быстрая справка

```bash
# Запуск
./start.sh              # Всё автоматически
./run.sh                # Только запуск
make run                # Через Make

# Настройка
./setup.sh              # Настроить окружение
make setup              # Через Make

# Docker
./docker-run.sh         # Запуск
docker-compose logs -f  # Логи
docker-compose down     # Остановка

# Тесты
make test               # Запуск тестов
pytest tests/ -v        # Напрямую

# Очистка
make clean              # Очистить артефакты

# Помощь
make help               # Все Make команды
cat START_HERE.txt      # Быстрый старт
cat USAGE.md            # Подробное руководство
```

---

## Рекомендации

✅ **Для новичков**: используйте `./start.sh`

✅ **Для разработки**: используйте `./run.sh` или активируйте `venv` вручную

✅ **Для production**: используйте Docker (`./docker-run.sh`)

✅ **Для CI/CD**: используйте Make (`make setup && make test && make run`)

---

**Начните сейчас:**

```bash
./start.sh
```

🎉 **Успехов!**
