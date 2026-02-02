# NeuroGenesis

**«Растущий разум» с активной семантической памятью**

NeuroGenesis — это модульная система искусственного интеллекта с семантической памятью, способная к обучению и росту. Система использует векторные представления для хранения и поиска воспоминаний, а также механизмы консолидации для оптимизации памяти.

## Архитектура

```
neurogenesis/
├── core/           # Ядро системы
│   ├── mind.py     # Центральный оркестратор (Mind)
│   ├── config.py   # Конфигурация
│   └── types.py    # Типы данных (Memory, Thought, etc.)
├── memory/         # Модуль памяти
│   ├── store.py    # Хранилище с SQLite
│   ├── embeddings.py   # Генерация эмбеддингов
│   └── vector_store.py # Векторное хранилище (FAISS)
├── growth/         # Модуль роста и обучения
│   ├── consolidator.py # Консолидация памяти
│   └── patterns.py     # Распознавание паттернов
├── api/            # REST API
│   ├── app.py      # FastAPI приложение
│   └── routes.py   # API эндпоинты
└── utils/          # Утилиты
    └── logging.py  # Структурированное логирование
```

## Основные концепции

### Memory (Память)
- **Semantic** — факты и концепции
- **Episodic** — события и опыт
- **Procedural** — навыки и процедуры
- **Working** — краткосрочная активная память

### Mind (Разум)
Центральный компонент, управляющий:
- Хранением и извлечением воспоминаний
- Семантическим поиском
- Ассоциативными связями
- Циклами роста и консолидации

### Growth (Рост)
- Консолидация памяти (укрепление важных воспоминаний)
- Затухание неиспользуемых воспоминаний
- Формирование паттернов и абстракций

## Установка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd neurogenesis

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или: venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Скопировать конфигурацию
cp .env.example .env
```

## Использование

### Программный интерфейс

```python
import asyncio
from neurogenesis import Mind

async def main():
    async with Mind() as mind:
        # Запомнить информацию
        memory = await mind.remember(
            content="Python — язык программирования",
            importance=0.8,
            tags=["programming", "python"],
        )
        
        # Вспомнить по запросу
        memories = await mind.recall(
            query="языки программирования",
            limit=5,
        )
        
        # Обработать мысль
        thought = await mind.think("Что я знаю о Python?")
        print(thought.generated_response)
        
        # Запустить цикл роста
        metrics = await mind.grow()
        print(f"Активных воспоминаний: {metrics.active_memories}")

asyncio.run(main())
```

### REST API

```bash
# Запустить сервер
python -m neurogenesis.main

# API доступен на http://localhost:8000
```

#### Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/remember` | Сохранить воспоминание |
| POST | `/api/v1/recall` | Найти воспоминания |
| POST | `/api/v1/think` | Обработать мысль |
| POST | `/api/v1/grow` | Запустить цикл роста |
| GET | `/api/v1/metrics` | Получить метрики |
| GET | `/api/v1/memory/{id}` | Получить воспоминание |
| DELETE | `/api/v1/memory/{id}` | Забыть воспоминание |

#### Примеры запросов

```bash
# Сохранить воспоминание
curl -X POST http://localhost:8000/api/v1/remember \
  -H "Content-Type: application/json" \
  -d '{"content": "Москва — столица России", "tags": ["geography"]}'

# Найти воспоминания
curl -X POST http://localhost:8000/api/v1/recall \
  -H "Content-Type: application/json" \
  -d '{"query": "столицы стран"}'

# Обработать мысль
curl -X POST http://localhost:8000/api/v1/think \
  -H "Content-Type: application/json" \
  -d '{"content": "Что я знаю о географии?"}'
```

## Разработка

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=neurogenesis --cov-report=html

# Конкретный модуль
pytest tests/test_memory.py -v
```

### Форматирование и линтинг

```bash
# Форматирование
black neurogenesis tests

# Линтинг
ruff check neurogenesis tests

# Проверка типов
mypy neurogenesis
```

## Конфигурация

Настройки через переменные окружения или `.env` файл:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `API_HOST` | Хост API | `0.0.0.0` |
| `API_PORT` | Порт API | `8000` |
| `MEMORY_DB_PATH` | Путь к БД | `./data/memory.db` |
| `VECTOR_STORE_PATH` | Путь к векторам | `./data/vectors` |
| `EMBEDDING_MODEL` | Модель эмбеддингов | `all-MiniLM-L6-v2` |
| `CONSOLIDATION_THRESHOLD` | Порог консолидации | `100` |
| `DECAY_RATE` | Скорость затухания | `0.01` |

## Лицензия

MIT License
