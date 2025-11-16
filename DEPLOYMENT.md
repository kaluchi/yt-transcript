# Руководство по развертыванию YouTube Transcript Bot

## Предварительные требования

### Получение API ключей

#### 1. Telegram Bot Token
1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен (формат: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

#### 2. YouTube Data API v3 Key
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите YouTube Data API v3:
   - Перейдите в "APIs & Services" > "Library"
   - Найдите "YouTube Data API v3"
   - Нажмите "Enable"
4. Создайте credentials:
   - "APIs & Services" > "Credentials"
   - "Create Credentials" > "API Key"
   - Сохраните ключ

#### 3. Anthropic API Key
1. Зарегистрируйтесь на [Anthropic Console](https://console.anthropic.com/)
2. Перейдите в "API Keys"
3. Создайте новый API ключ
4. Сохраните ключ (формат: `sk-ant-...`)

## Развертывание

### Вариант 1: Docker (Рекомендуется)

#### Шаг 1: Подготовка
```bash
# Клонировать репозиторий
git clone <your-repo-url>
cd yt-transcript

# Создать .env файл
cp .env.example .env
```

#### Шаг 2: Настройка .env
Отредактируйте `.env` файл:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
YOUTUBE_API_KEY=your_youtube_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DATABASE_URL=sqlite:///./data/bot.db
LOG_LEVEL=INFO
```

#### Шаг 3: Запуск
```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down
```

#### Обновление
```bash
# Остановить контейнер
docker-compose down

# Получить обновления
git pull

# Пересобрать и запустить
docker-compose up -d --build
```

### Вариант 2: Локальный запуск

#### Шаг 1: Установка зависимостей
```bash
# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

#### Шаг 2: Настройка
```bash
# Создать .env файл
cp .env.example .env

# Отредактировать .env (добавить API ключи)
nano .env  # или любой текстовый редактор
```

#### Шаг 3: Проверка конфигурации
```bash
python scripts/check_config.py
```

#### Шаг 4: Запуск
```bash
# Простой запуск
python -m src.bot

# Или через скрипт
./start.sh
```

### Вариант 3: Системный сервис (Linux)

#### Создание systemd service
```bash
sudo nano /etc/systemd/system/yt-transcript-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=YouTube Transcript Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/yt-transcript
Environment="PATH=/path/to/yt-transcript/venv/bin"
ExecStart=/path/to/yt-transcript/venv/bin/python -m src.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация:
```bash
# Перезагрузить systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable yt-transcript-bot

# Запустить сервис
sudo systemctl start yt-transcript-bot

# Проверить статус
sudo systemctl status yt-transcript-bot

# Просмотр логов
sudo journalctl -u yt-transcript-bot -f
```

## Мониторинг и обслуживание

### Логи

#### Docker
```bash
docker-compose logs -f bot
```

#### Локальный запуск
Логи выводятся в stdout. Для сохранения в файл:
```bash
python -m src.bot 2>&1 | tee bot.log
```

### База данных

База данных SQLite хранится в `data/bot.db`

#### Резервное копирование
```bash
# Docker
docker-compose exec bot cp /app/data/bot.db /app/data/bot.db.backup

# Локально
cp data/bot.db data/bot.db.backup
```

#### Восстановление
```bash
cp data/bot.db.backup data/bot.db
```

### Обновление зависимостей

```bash
# Просмотр устаревших пакетов
pip list --outdated

# Обновление конкретного пакета
pip install --upgrade package-name

# Обновление requirements.txt
pip freeze > requirements.txt
```

## Безопасность

### Рекомендации

1. **Защита .env файла**
   ```bash
   chmod 600 .env
   ```

2. **Использование secrets в production**
   - Для Docker: Docker secrets или переменные окружения
   - Для Kubernetes: Secrets
   - Для облака: AWS Secrets Manager, Azure Key Vault и т.д.

3. **Регулярное обновление**
   - Проверяйте обновления безопасности
   - Обновляйте зависимости
   - Следите за CVE

4. **Ограничение доступа**
   - Используйте firewall
   - Ограничьте сетевой доступ к серверу
   - Используйте SSH ключи вместо паролей

5. **Мониторинг**
   - Настройте алерты на ошибки
   - Следите за использованием ресурсов
   - Мониторьте API квоты

## Решение проблем

### Бот не запускается

1. **Проверьте .env файл**
   ```bash
   python scripts/check_config.py
   ```

2. **Проверьте логи**
   ```bash
   # Docker
   docker-compose logs bot

   # Systemd
   sudo journalctl -u yt-transcript-bot -n 100
   ```

3. **Проверьте сетевое соединение**
   ```bash
   ping api.telegram.org
   ping www.googleapis.com
   ping api.anthropic.com
   ```

### Превышены квоты YouTube API

YouTube API имеет лимит 10,000 единиц в день. Одна операция `videos.list` стоит ~1 единицу.

**Решение:**
1. Запросите увеличение квоты в Google Cloud Console
2. Используйте кэширование (уже реализовано в боте)
3. Мониторьте использование в Google Cloud Console

### Ошибки Anthropic API

**Превышен rate limit:**
- Добавьте задержки между запросами
- Используйте exponential backoff

**Недостаточно средств:**
- Пополните баланс в Anthropic Console

### База данных заблокирована

SQLite может блокироваться при одновременном доступе.

**Решение:**
- Перезапустите бота
- Для production рассмотрите использование PostgreSQL

## Масштабирование

### Переход на PostgreSQL

1. **Установка PostgreSQL**
   ```bash
   # Docker
   docker run -d \
     --name postgres \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=ytbot \
     -p 5432:5432 \
     postgres:15
   ```

2. **Обновление .env**
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/ytbot
   ```

3. **Установка драйвера**
   ```bash
   pip install psycopg2-binary
   ```

### Использование Redis для кэширования

```bash
# Добавить в docker-compose.yml
redis:
  image: redis:7
  ports:
    - "6379:6379"
```

### Горизонтальное масштабирование

Для обработки большого количества пользователей:
1. Используйте очереди сообщений (RabbitMQ, Redis Queue)
2. Запустите несколько экземпляров воркеров
3. Используйте load balancer

## Производительность

### Оптимизация

1. **Кэширование транскриптов** (уже реализовано)
2. **Ограничение длины транскрипта** для AI
3. **Асинхронная обработка** (уже реализовано)
4. **Индексы базы данных** (уже реализовано)

### Мониторинг метрик

Рекомендуемые инструменты:
- Prometheus + Grafana
- Datadog
- New Relic

## Поддержка

Для вопросов и багов создавайте Issues в репозитории.

## Чеклист для production

- [ ] API ключи настроены
- [ ] .env файл защищен (chmod 600)
- [ ] Настроено резервное копирование БД
- [ ] Настроены логи
- [ ] Настроен мониторинг
- [ ] Настроен systemd service или Docker
- [ ] Firewall настроен
- [ ] SSL/TLS настроен (если используется webhook)
- [ ] Документация обновлена
- [ ] Команда знает как перезапустить бота
