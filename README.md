# NeuroGenesis

Проект: «растущий разум» с активной семантической памятью.

Пока что это базовый каркас (пакет + CLI + тесты + CI), чтобы дальше быстро наращивать функциональность.

## Быстрый старт

Требования: Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## CLI

Хранилище — JSONL файл (по умолчанию `memory.jsonl` в корне).

Добавить запись:

```bash
neurogenesis add "кошка пьёт молоко" --meta '{"source":"demo"}'
```

Запрос:

```bash
neurogenesis query "кошка молоко" --top-k 5
```
