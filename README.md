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

Экспортируйте переменные окружения с префиксом `YT_TRANSCRIPT_*`:

```bash
export YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
export YT_TRANSCRIPT_YOUTUBE_API_KEY=your_youtube_api_key_here
export YT_TRANSCRIPT_OPENAI_API_KEY=your_openai_api_key_here
```

**Для локального запуска:**

Экспортируйте переменные окружения:

```bash
export TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
export YOUTUBE_API_KEY=your_youtube_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Запуск с Docker

```bash
make docker-up
```

Пересборка при изменениях:

```bash
make docker-build && make docker-up
```

Просмотр логов:

```bash
make docker-logs
```

Остановка:

```bash
make docker-down
```

### 4. Запуск локально (для разработки)

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Linux/Mac)
source venv/bin/activate

# Активация (Windows PowerShell)
venv\Scripts\activate

# Установка зависимостей
make install

# Запуск бота
make run
```

## Доступные команды (Makefile)

Для удобства все основные операции доступны через `make`:

```bash
make help          # Показать все доступные команды
make install       # Установить зависимости (требует активный venv)
make test          # Запустить тесты
make coverage      # Запустить тесты с отчетом о покрытии
make lint          # Проверить синтаксис кода
make run           # Запустить бота локально
make docker-build  # Собрать Docker образ
make docker-up     # Запустить в Docker
make docker-down   # Остановить Docker контейнер
make docker-logs   # Показать логи Docker контейнера
make clean         # Удалить временные файлы
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

```bash
make test                           # Все тесты (56 тестов)
make coverage                       # С покрытием кода (96%)
make lint                           # Проверка синтаксиса
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

```bash
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Ограничения

- Транскрипты доступны только для видео, где они включены
- YouTube API имеет квоты (10,000 единиц в день по умолчанию)
- GPT API имеет лимиты по токенам
- Длинные транскрипты обрезаются для соответствия лимитам API
