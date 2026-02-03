# Быстрый старт NeuroGenesis 🚀

## Три простых шага

### Шаг 1: Клонирование репозитория
```bash
git clone <repository-url>
cd NeuroGenesis
```

### Шаг 2: Настройка
```bash
./setup.sh
```

Этот скрипт:
- Создаст виртуальное окружение Python
- Установит все необходимые зависимости
- Создаст структуру директорий
- Настроит конфигурационные файлы

### Шаг 3: Запуск
```bash
./run.sh
```

## Что дальше?

После успешного запуска вы увидите приветственное сообщение и системную информацию.

## Альтернативный способ: Docker

Если у вас установлен Docker:

```bash
./docker-run.sh
```

Это всё! Docker автоматически создаст и запустит изолированный контейнер со всеми зависимостями.

## Возможные проблемы

### Ошибка: "Permission denied"
```bash
chmod +x setup.sh run.sh docker-run.sh
```

### Ошибка: "Python not found"
Установите Python 3.8 или выше:
- Ubuntu/Debian: `sudo apt install python3 python3-pip python3-venv`
- macOS: `brew install python3`
- Windows: скачайте с python.org

### Ошибка при установке зависимостей
Если установка torch или других больших библиотек занимает много времени или падает:
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## Нужна помощь?

Откройте issue в репозитории или обратитесь к документации в README.md.
