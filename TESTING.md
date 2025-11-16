# Руководство по тестированию

## Запуск тестов

### Быстрый запуск

```bash
# Все тесты
./run_tests.sh

# Или с make
make test
```

### Ручной запуск

```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Все тесты
pytest

# С подробным выводом
pytest -v

# Конкретный файл
pytest tests/test_youtube.py -v

# Конкретный тест
pytest tests/test_youtube.py::TestExtractVideoId::test_extract_from_watch_url -v
```

## Тесты с покрытием

```bash
# Генерация отчета покрытия
pytest --cov=src --cov-report=term-missing --cov-report=html

# Просмотр HTML отчета
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Структура тестов

### test_config.py
Тесты конфигурации:
- ✓ Загрузка из переменных окружения
- ✓ Значения по умолчанию
- ✓ Валидация обязательных полей

### test_database.py
Тесты базы данных:
- ✓ Сохранение и получение метаданных видео
- ✓ Сохранение и получение транскриптов
- ✓ Сохранение и получение саммари
- ✓ История диалогов
- ✓ Получение последнего видео пользователя

### test_youtube.py
Тесты YouTube сервиса:
- ✓ Извлечение video ID из различных форматов URL
- ✓ Парсинг длительности видео
- ✓ Получение метаданных
- ✓ Получение транскриптов
- ✓ Fallback на английский язык

### test_ai.py
Тесты AI сервиса:
- ✓ Генерация саммари
- ✓ Диалоги о видео
- ✓ Включение метаданных в промпт
- ✓ Управление историей диалогов

### test_bot.py
Тесты Telegram бота:
- ✓ Команды /start и /help
- ✓ Обработка YouTube URLs
- ✓ Обработка диалогов
- ✓ Обновление статусных сообщений
- ✓ Обработка ошибок

## Написание новых тестов

### Пример теста

```python
import pytest
from src.youtube import YouTubeService

@pytest.fixture
def youtube_service():
    """Create YouTube service for testing."""
    return YouTubeService(api_key="test_key")

def test_extract_video_id(youtube_service):
    """Test video ID extraction."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    video_id = youtube_service.extract_video_id(url)
    assert video_id == "dQw4w9WgXcQ"
```

### Использование моков

```python
from unittest.mock import Mock, patch

@patch('src.youtube.build')
def test_get_metadata(mock_build, youtube_service):
    """Test metadata fetching with mocked API."""
    mock_youtube = Mock()
    mock_build.return_value = mock_youtube

    mock_youtube.videos().list().execute.return_value = {
        "items": [{"id": "test", "snippet": {"title": "Test"}}]
    }

    # Your test code here
```

### Асинхронные тесты

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await some_async_function()
    assert result == expected_value
```

## Интеграционные тесты

### Тестирование с реальными API

Создайте `.env.test` файл с тестовыми ключами:

```env
TELEGRAM_BOT_TOKEN=test_token
YOUTUBE_API_KEY=real_youtube_key
OPENAI_API_KEY=real_openai_key
DATABASE_URL=sqlite:///./test.db
```

Запуск интеграционных тестов:

```bash
# С реальными API (осторожно - расходует квоты!)
pytest tests/integration/ -v --env-file=.env.test
```

## Тестирование вручную

### 1. Локальный запуск

```bash
# Запустить бота
./start.sh

# В Telegram:
# 1. Найти вашего бота
# 2. Отправить /start
# 3. Отправить YouTube ссылку
# 4. Задать вопросы о видео
```

### Тестовые сценарии

#### Сценарий 1: Новое видео
1. Отправить ссылку на YouTube видео
2. Проверить, что бот показывает прогресс
3. Проверить, что саммари отправлено
4. Задать вопрос о видео
5. Проверить, что ответ релевантен

#### Сценарий 2: Повторное видео
1. Отправить ссылку на уже обработанное видео
2. Проверить, что саммари отправлено сразу

#### Сценарий 3: Диалог
1. Отправить ссылку на видео
2. Задать несколько вопросов подряд
3. Проверить, что контекст сохраняется

#### Сценарий 4: Обработка ошибок
1. Отправить несуществующую ссылку
2. Проверить сообщение об ошибке
3. Отправить вопрос без предыдущего видео
4. Проверить сообщение-подсказку

### 2. Docker тестирование

```bash
# Собрать образ
docker-compose build

# Запустить
docker-compose up

# Проверить логи
docker-compose logs -f bot

# Остановить
docker-compose down
```

## Тестирование производительности

### Нагрузочное тестирование

```python
# tests/load/test_load.py
import asyncio
import time

async def test_concurrent_users():
    """Test with multiple concurrent users."""
    start = time.time()

    # Simulate 10 concurrent users
    tasks = [process_video(f"user_{i}") for i in range(10)]
    await asyncio.gather(*tasks)

    duration = time.time() - start
    print(f"Processed 10 users in {duration:.2f}s")
    assert duration < 60  # Should complete in under 60s
```

### Профилирование

```bash
# Профилирование с cProfile
python -m cProfile -o profile.stats -m src.bot

# Анализ результатов
python -m pstats profile.stats
```

## CI/CD Integration

### GitHub Actions пример

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Метрики качества

### Целевые показатели

- **Покрытие кода:** ≥ 80%
- **Все тесты:** Проходят ✓
- **Flake8:** Без ошибок
- **MyPy:** Без ошибок типов (если используется)

### Проверка качества

```bash
# Покрытие
pytest --cov=src --cov-report=term-missing

# Стиль кода (если установлен flake8)
flake8 src/ tests/

# Типы (если установлен mypy)
mypy src/
```

## Отладка тестов

### Запуск с отладчиком

```bash
# С pdb
pytest --pdb

# Остановиться на первой ошибке
pytest -x

# Показать print statements
pytest -s

# Подробный вывод
pytest -vv
```

### Логирование в тестах

```python
import logging

def test_with_logging(caplog):
    """Test with captured logs."""
    with caplog.at_level(logging.INFO):
        # Your code here
        pass

    assert "Expected log message" in caplog.text
```

## Чеклист перед коммитом

- [ ] Все тесты проходят
- [ ] Новый код покрыт тестами
- [ ] Документация обновлена
- [ ] Нет warnings в тестах
- [ ] Код отформатирован
- [ ] Commit message описательный

## Полезные команды

```bash
# Запустить только failed тесты
pytest --lf

# Запустить только новые тесты
pytest --nf

# Параллельный запуск (если установлен pytest-xdist)
pytest -n auto

# Генерация HTML отчета
pytest --html=report.html

# Замер времени выполнения тестов
pytest --durations=10
```
