# Руководство по использованию NeuroGenesis

## 🚀 Как запустить проект

### Самый простой способ

Запустите **один скрипт**, который делает всё автоматически:

```bash
./start.sh
```

Этот скрипт:
1. ✅ Проверит, установлен ли Python 3
2. ✅ Создаст виртуальное окружение
3. ✅ Установит все зависимости (PyTorch, Transformers и др.)
4. ✅ Создаст структуру директорий
5. ✅ Настроит конфигурацию
6. ✅ Запустит приложение

### Другие способы запуска

#### 1. Раздельная настройка и запуск

```bash
# Первый раз - настройка
./setup.sh

# Каждый последующий запуск
./run.sh
```

#### 2. Использование Make

```bash
# Показать все доступные команды
make help

# Настройка
make setup

# Запуск
make run

# Тесты
make test

# Очистка
make clean
```

#### 3. Docker (изолированное окружение)

```bash
# Запуск в Docker
./docker-run.sh

# Или напрямую через docker-compose
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

#### 4. Ручной запуск

```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Запустить приложение
python3 src/main.py
```

## 📁 Структура проекта

```
NeuroGenesis/
│
├── 🚀 Скрипты запуска
│   ├── start.sh           # Главный скрипт - всё в одном
│   ├── setup.sh           # Только настройка
│   ├── run.sh             # Только запуск
│   └── docker-run.sh      # Запуск через Docker
│
├── ⚙️ Конфигурация
│   ├── Makefile           # Команды Make
│   ├── requirements.txt   # Python зависимости
│   ├── .env.example       # Пример конфигурации
│   ├── Dockerfile         # Docker образ
│   └── docker-compose.yml # Docker Compose
│
├── 📚 Документация
│   ├── README.md          # Основная документация
│   ├── QUICK_START.md     # Быстрый старт
│   └── USAGE.md           # Это руководство
│
├── 💻 Исходный код
│   └── src/
│       ├── main.py        # Точка входа
│       ├── core/          # Ядро системы
│       ├── memory/        # Семантическая память
│       └── utils/         # Утилиты
│
├── 🧪 Тесты
│   └── tests/
│       └── test_basic.py
│
└── 📦 Данные (создаются автоматически)
    ├── data/              # Датасеты
    ├── models/            # Обученные модели
    ├── logs/              # Логи работы
    └── config/            # Конфигурации
```

## 🛠️ Доступные команды

### Через скрипты

```bash
./start.sh        # Полная настройка и запуск
./setup.sh        # Только настройка окружения
./run.sh          # Только запуск приложения
./docker-run.sh   # Запуск в Docker
```

### Через Make

```bash
make help         # Показать справку
make setup        # Настройка
make run          # Запуск
make test         # Тесты
make clean        # Очистка
make docker-build # Сборка Docker образа
make docker-run   # Запуск в Docker
make docker-stop  # Остановка Docker
```

### Через Python напрямую

```bash
# Активировать окружение
source venv/bin/activate

# Запустить main.py
python3 src/main.py

# Запустить тесты
pytest tests/ -v

# Установить новые пакеты
pip install <package-name>
pip freeze > requirements.txt
```

## ⚙️ Конфигурация

### Файл .env

Создайте файл `.env` (или скопируйте `.env.example`):

```bash
cp .env.example .env
```

Основные настройки:

```bash
# Режим отладки
DEBUG=True

# Уровень логирования (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Директории
DATA_DIR=./data
MODELS_DIR=./models
LOGS_DIR=./logs
```

## 🐛 Решение проблем

### Ошибка: "Permission denied"

```bash
chmod +x *.sh
```

### Ошибка: "Python not found"

Установите Python 3.8+:
- **Ubuntu/Debian**: `sudo apt install python3 python3-pip python3-venv`
- **macOS**: `brew install python3`
- **Windows**: скачайте с [python.org](https://python.org)

### Ошибка при установке зависимостей

```bash
# Очистите кеш pip
pip cache purge

# Обновите pip
pip install --upgrade pip

# Установите заново
pip install -r requirements.txt --no-cache-dir
```

### Ошибка: "Virtual environment not found"

```bash
# Запустите setup.sh
./setup.sh

# Или создайте вручную
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Проблемы с Docker

```bash
# Проверьте, запущен ли Docker
docker --version
docker ps

# Пересоберите образ
docker-compose build --no-cache

# Очистите старые контейнеры
docker-compose down -v
docker-compose up -d
```

## 📊 Что дальше?

После успешного запуска вы можете:

1. **Изучить код** в директории `src/`
2. **Добавить свою логику** в `src/main.py`
3. **Реализовать семантическую память** в `src/memory/`
4. **Добавить нейронные сети** в `src/core/`
5. **Написать тесты** в `tests/`
6. **Настроить логирование** в `.env`

## 💡 Полезные команды

```bash
# Показать версию Python
python3 --version

# Показать установленные пакеты
pip list

# Проверить структуру проекта
tree -L 2  # или: ls -R

# Просмотреть логи
tail -f logs/*.log

# Активировать окружение
source venv/bin/activate

# Деактивировать окружение
deactivate
```

## 📝 Примеры использования

### Пример 1: Первый запуск

```bash
# Скачайте проект
git clone <repository-url>
cd NeuroGenesis

# Запустите всё одной командой
./start.sh
```

### Пример 2: Разработка

```bash
# Активируйте окружение
source venv/bin/activate

# Отредактируйте код
nano src/main.py

# Запустите
python3 src/main.py

# Запустите тесты
pytest tests/
```

### Пример 3: Производственный запуск

```bash
# Запустите в Docker
./docker-run.sh

# Проверьте статус
docker-compose ps

# Просмотрите логи
docker-compose logs -f
```

## 🆘 Поддержка

Если у вас возникли проблемы:

1. Проверьте документацию в `README.md`
2. Посмотрите `QUICK_START.md`
3. Изучите логи в `logs/`
4. Откройте issue в репозитории

---

**Успешной работы с NeuroGenesis! 🧠✨**
