# YouTube Transcript Bot

Telegram bot для получения транскриптов видео с YouTube и обсуждения их с помощью AI.

## Возможности

- Получение метаданных видео с YouTube
- Скачивание транскриптов (на языке пользователя или на английском)
- Автоматическое создание саммари видео (до 500 слов)
- Интеллектуальные диалоги о содержании видео с сохранением контекста
- Кэширование обработанных видео для быстрого доступа
- Отображение прогресса обработки в реальном времени

## Требования

- Python 3.11+
- Docker и Docker Compose (для контейнеризации)
- Telegram Bot Token
- YouTube Data API v3 Key
- OpenAI API Key (GPT)

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd yt-transcript
```

### 2. Настройка переменных окружения

**Для Docker (рекомендуется):**

*Linux/Mac:*
```bash
export YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
export YT_TRANSCRIPT_YOUTUBE_API_KEY=your_youtube_api_key_here
export YT_TRANSCRIPT_OPENAI_API_KEY=your_openai_api_key_here
```

*Windows PowerShell:*
```powershell
$env:YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"
$env:YT_TRANSCRIPT_YOUTUBE_API_KEY="your_youtube_api_key_here"
$env:YT_TRANSCRIPT_OPENAI_API_KEY="your_openai_api_key_here"
```

**Для локального запуска:**

*Linux/Mac:*
```bash
export TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
export YOUTUBE_API_KEY=your_youtube_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here
```

*Windows PowerShell:*
```powershell
$env:TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"
$env:YOUTUBE_API_KEY="your_youtube_api_key_here"
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. Запуск с Docker

**Linux/Mac:**
```bash
make docker-up                         # Запуск
make docker-build && make docker-up    # Пересборка и запуск
make docker-logs                       # Просмотр логов
make docker-down                       # Остановка
```

**Windows PowerShell:**
```powershell
docker compose up -d                   # Запуск
docker compose build; docker compose up -d  # Пересборка и запуск
docker compose logs -f bot             # Просмотр логов
docker compose down                    # Остановка
```

### 4. Запуск локально (для разработки)

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
make install
make run
```

**Windows:**

*Вариант 1: Установить make (рекомендуется)*
```powershell
# Установка через Chocolatey
choco install make

# Или через Scoop
scoop install make

# После установки используйте команды make как на Linux
python -m venv venv
venv\Scripts\activate
make install
make run
```

*Вариант 2: Без make*
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m src.bot
```

## Доступные команды

**Linux/Mac (Makefile):**
```bash
make help          # Показать все доступные команды
make install       # Установить зависимости
make test          # Запустить тесты
make coverage      # Тесты с отчетом о покрытии
make lint          # Проверить синтаксис
make run           # Запустить бота
make docker-build  # Собрать Docker образ
make docker-up     # Запустить в Docker
make docker-down   # Остановить Docker
make docker-logs   # Показать логи
make clean         # Удалить временные файлы
```

**Windows PowerShell:**
```powershell
pip install -r requirements.txt           # Установить зависимости
python -m pytest -v                       # Запустить тесты
python -m pytest --cov=src --cov-report=html  # Тесты с покрытием
python -m py_compile src/*.py tests/*.py  # Проверить синтаксис
python -m src.bot                         # Запустить бота
docker compose build                      # Собрать Docker образ
docker compose up -d                      # Запустить в Docker
docker compose down                       # Остановить Docker
docker compose logs -f bot                # Показать логи
```

## Использование

### Команды бота

- `/start` - Приветственное сообщение и инструкции
- `/help` - Справка по использованию

### Основной workflow

1. **Отправьте ссылку на YouTube видео:**
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```
   Бот:
   - Скачает метаданные видео
   - Получит транскрипт (на вашем языке или английском)
   - Создаст краткое саммари
   - Отправит вам результат

2. **Задавайте вопросы о видео:**
   ```
   О чем это видео?
   Что говорится про...?
   Можешь объяснить часть про...?
   ```
   Бот помнит контекст беседы и отвечает на основе транскрипта.

3. **Повторный доступ:**
   Если видео уже обработано, бот сразу отдаст сохраненное саммари.

## Архитектура

```
src/
├── bot.py          # Telegram bot handlers
├── youtube.py      # YouTube API & transcript service
├── ai.py           # AI service (GPT)
├── database.py     # Database operations (SQLAlchemy)
├── models.py       # Data models
└── config.py       # Configuration management

tests/
├── test_bot.py
├── test_youtube.py
├── test_ai.py
├── test_database.py
└── test_config.py
```

## Тестирование

**Linux/Mac:**
```bash
make test          # Все тесты (56 тестов, 96% покрытие)
make coverage      # С HTML отчетом
make lint          # Проверка синтаксиса
```

**Windows PowerShell:**
```powershell
python -m pytest -v                              # Все тесты
python -m pytest --cov=src --cov-report=html     # С HTML отчетом
python -m py_compile src/*.py tests/*.py         # Проверка синтаксиса
```

## База данных

Бот использует SQLite для хранения:

- Метаданных видео (название, канал, просмотры и т.д.)
- Транскриптов (на разных языках)
- Саммари видео
- Истории диалогов пользователей

База данных автоматически создается при первом запуске.

## Логирование

Логи выводятся в stdout. Настройте уровень логирования через переменную `LOG_LEVEL`:

**Linux/Mac:**
```bash
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Windows PowerShell:**
```powershell
$env:LOG_LEVEL="DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Ограничения

- Транскрипты доступны только для видео, где они включены
- YouTube API имеет квоты (10,000 единиц в день по умолчанию)
- GPT API имеет лимиты по токенам
- Длинные транскрипты обрезаются для соответствия лимитам API
