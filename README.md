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

Или используйте файл `.env.docker`:

```bash
cp .env.docker.example .env.docker
# Отредактируйте .env.docker с вашими ключами
source .env.docker
```

**Для локального запуска:**

```bash
cp .env.example .env
# Отредактируйте .env с вашими ключами
```

### 3. Запуск с Docker

```bash
# С автоматической проверкой переменных окружения
./docker-start.sh

# Или напрямую
docker-compose up -d
```

Или пересборка при изменениях:

```bash
docker-compose up --build -d
```

### 4. Запуск локально (для разработки)

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск бота
python -m src.bot
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

Запуск всех тестов:

```bash
pytest
```

С покрытием кода:

```bash
pytest --cov=src --cov-report=html
```

Запуск конкретного теста:

```bash
pytest tests/test_youtube.py -v
```

## Разработка

### Структура кода

- **bot.py**: Основная логика бота, обработчики команд и сообщений
- **youtube.py**: Работа с YouTube API и получение транскриптов
- **ai.py**: Интеграция с OpenAI GPT для саммари и диалогов
- **database.py**: SQLAlchemy модели и операции с базой данных
- **models.py**: Dataclass модели для типизации данных
- **config.py**: Управление конфигурацией из переменных окружения

### Основные зависимости

- `python-telegram-bot` - Telegram Bot API
- `youtube-transcript-api` - Получение транскриптов
- `google-api-python-client` - YouTube Data API
- `openai` - GPT API
- `sqlalchemy` - ORM для базы данных
- `pytest` - Тестирование

## База данных

Бот использует SQLite для хранения:

- Метаданных видео (название, канал, просмотры и т.д.)
- Транскриптов (на разных языках)
- Саммари видео
- Истории диалогов пользователей

База данных автоматически создается при первом запуске.

## Логирование

Логи выводятся в stdout и могут быть настроены через переменную `LOG_LEVEL`:

```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

При запуске в Docker логи доступны через:

```bash
docker-compose logs -f bot
```

## Ограничения

- Транскрипты доступны только для видео, где они включены
- YouTube API имеет квоты (10,000 единиц в день по умолчанию)
- GPT API имеет лимиты по токенам
- Длинные транскрипты обрезаются для соответствия лимитам API

## Безопасность

- Храните `.env` файл в безопасности (не коммитьте его в git)
- Используйте отдельные API ключи для разработки и продакшена
- Регулярно ротируйте API ключи
- Ограничьте права доступа к базе данных

## Troubleshooting

### Бот не запускается

1. Проверьте `.env` файл и наличие всех ключей
2. Убедитесь, что все зависимости установлены
3. Проверьте логи: `docker-compose logs bot`

### Ошибки YouTube API

- Проверьте квоты в Google Cloud Console
- Убедитесь, что YouTube Data API v3 включен
- Проверьте правильность API ключа

### Ошибки OpenAI API

- Проверьте баланс аккаунта
- Убедитесь в правильности API ключа
- Проверьте rate limits

## Лицензия

MIT

## Вклад

Pull requests приветствуются! Для значительных изменений сначала откройте issue для обсуждения.

## Автор

Created with GPT Code
