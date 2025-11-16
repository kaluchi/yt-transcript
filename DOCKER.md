# Docker Deployment Guide

## Быстрый старт

### 1. Установите переменные окружения

Docker-compose **НЕ** использует файл `.env` внутри контейнера.
Вместо этого он читает переменные с **хоста** с префиксом `YT_TRANSCRIPT_*`.

```bash
# Установите переменные на хосте
export YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
export YT_TRANSCRIPT_YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
export YT_TRANSCRIPT_OPENAI_API_KEY=sk-proj-03-XXXXXXXXXXXXXXXXXXXXXXXX
```

### 2. Запустите бота

```bash
# Простой запуск
docker-compose up -d

# Или с автоматической проверкой
./docker-start.sh
```

### 3. Проверьте логи

```bash
docker-compose logs -f bot
```

---

## Способы установки переменных окружения

### Способ 1: Временный (на текущую сессию)

```bash
export YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN=your_token
export YT_TRANSCRIPT_YOUTUBE_API_KEY=your_key
export YT_TRANSCRIPT_OPENAI_API_KEY=your_key
docker-compose up -d
```

**Недостаток:** Переменные исчезнут после закрытия терминала.

---

### Способ 2: Использование .env.docker файла

```bash
# 1. Создайте файл из примера
cp .env.docker.example .env.docker

# 2. Отредактируйте .env.docker
nano .env.docker

# 3. Загрузите переменные в текущую сессию
source .env.docker

# 4. Запустите бота
docker-compose up -d
```

Содержимое `.env.docker`:
```bash
export YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
export YT_TRANSCRIPT_YOUTUBE_API_KEY=your_youtube_api_key_here
export YT_TRANSCRIPT_OPENAI_API_KEY=your_openai_api_key_here
```

**Преимущество:** Ключи в одном месте, можно версионировать (но добавьте в .gitignore!)

---

### Способ 3: Постоянные переменные (в .bashrc/.zshrc)

Добавьте в `~/.bashrc` или `~/.zshrc`:

```bash
# YouTube Transcript Bot
export YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN=your_token
export YT_TRANSCRIPT_YOUTUBE_API_KEY=your_key
export YT_TRANSCRIPT_OPENAI_API_KEY=your_key
```

Затем:
```bash
source ~/.bashrc  # или ~/.zshrc
docker-compose up -d
```

**Преимущество:** Переменные доступны во всех терминалах навсегда.
**Недостаток:** Ключи в файле конфигурации shell (будьте осторожны).

---

### Способ 4: Systemd Environment File

Для production серверов с systemd:

```bash
# Создайте файл с переменными
sudo nano /etc/youtube-transcript-bot.env
```

Содержимое:
```
YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN=your_token
YT_TRANSCRIPT_YOUTUBE_API_KEY=your_key
YT_TRANSCRIPT_OPENAI_API_KEY=your_key
```

Systemd service:
```ini
[Unit]
Description=YouTube Transcript Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/yt-transcript
EnvironmentFile=/etc/youtube-transcript-bot.env
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

---

## Проверка переменных

### Скрипт docker-start.sh

Используйте встроенный скрипт для автоматической проверки:

```bash
./docker-start.sh
```

Скрипт проверит:
- ✅ Все обязательные переменные установлены
- ✅ Docker и docker-compose доступны
- ✅ Автоматически запустит контейнеры

### Ручная проверка

```bash
# Проверьте, что переменные установлены
echo $YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN
echo $YT_TRANSCRIPT_YOUTUBE_API_KEY
echo $YT_TRANSCRIPT_OPENAI_API_KEY

# Проверьте, что docker-compose видит их
docker-compose config
```

---

## Опциональные переменные

### DATABASE_URL

По умолчанию: `sqlite:///./data/bot.db`

Изменить на PostgreSQL:
```bash
export YT_TRANSCRIPT_DATABASE_URL=postgresql://user:password@localhost:5432/ytbot
```

### LOG_LEVEL

По умолчанию: `INFO`

Варианты: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

```bash
export YT_TRANSCRIPT_LOG_LEVEL=DEBUG
```

---

## Управление контейнером

### Запуск

```bash
# Запустить в фоне
docker-compose up -d

# Запустить с пересборкой
docker-compose up -d --build

# Запустить и смотреть логи
docker-compose up
```

### Остановка

```bash
# Остановить контейнер
docker-compose stop

# Остановить и удалить контейнер
docker-compose down

# Остановить, удалить контейнер и volumes (УДАЛИТ БД!)
docker-compose down -v
```

### Логи

```bash
# Смотреть логи в реальном времени
docker-compose logs -f bot

# Последние 100 строк
docker-compose logs --tail=100 bot

# Логи с временными метками
docker-compose logs -f -t bot
```

### Перезапуск

```bash
# Перезапустить контейнер
docker-compose restart bot

# Обновить код и перезапустить
git pull
docker-compose up -d --build
```

---

## Обновление бота

### Обновление без остановки сервиса

```bash
# 1. Получить обновления
git pull

# 2. Пересобрать образ
docker-compose build

# 3. Пересоздать контейнер
docker-compose up -d
```

Docker автоматически:
- Создаст новый контейнер
- Переключит трафик
- Удалит старый контейнер

База данных сохранится (она в volume).

---

## Резервное копирование

### База данных

```bash
# Создать backup
docker-compose exec bot cp /app/data/bot.db /app/data/bot.db.backup

# Скопировать на хост
docker cp youtube-transcript-bot:/app/data/bot.db.backup ./backup-$(date +%Y%m%d).db

# Восстановить из backup
docker cp backup-20250116.db youtube-transcript-bot:/app/data/bot.db
docker-compose restart bot
```

### Автоматический backup (cron)

```bash
# Создайте скрипт
cat > /opt/backup-ytbot.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/backups/yt-transcript
DATE=$(date +%Y%m%d-%H%M%S)
mkdir -p $BACKUP_DIR
docker cp youtube-transcript-bot:/app/data/bot.db $BACKUP_DIR/bot-$DATE.db
# Удалить backup старше 30 дней
find $BACKUP_DIR -name "bot-*.db" -mtime +30 -delete
EOF

chmod +x /opt/backup-ytbot.sh

# Добавьте в cron (каждый день в 3 утра)
crontab -e
# 0 3 * * * /opt/backup-ytbot.sh
```

---

## Troubleshooting

### Ошибка: переменные не установлены

```
Error: YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN is not set
```

**Решение:**
```bash
# Проверьте переменные
env | grep YT_TRANSCRIPT

# Если пусто - установите
export YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN=your_token
```

### Ошибка: контейнер не запускается

```bash
# Посмотрите логи
docker-compose logs bot

# Проверьте конфигурацию
docker-compose config

# Пересоздайте контейнер
docker-compose down
docker-compose up -d --build
```

### База данных заблокирована

```bash
# Перезапустите контейнер
docker-compose restart bot

# Если не помогло - остановите все процессы
docker-compose down
docker-compose up -d
```

### Недостаточно места на диске

```bash
# Очистите неиспользуемые образы
docker system prune -a

# Проверьте размер данных
du -sh ./data/
```

---

## Production Deployment

### Рекомендуемая конфигурация

```bash
# 1. Используйте systemd
sudo cp systemd/yt-transcript-bot.service /etc/systemd/system/
sudo systemctl enable yt-transcript-bot
sudo systemctl start yt-transcript-bot

# 2. Настройте мониторинг
# (Prometheus, Grafana, или ваш инструмент)

# 3. Настройте алерты
# (Email, Slack, Telegram при падении бота)

# 4. Настройте автоматический backup
# (Cron job каждый день)

# 5. Настройте логирование
# (Loki, ELK stack, или CloudWatch)
```

### Безопасность

```bash
# 1. Защитите .env.docker
chmod 600 .env.docker

# 2. Не коммитьте секреты
echo '.env.docker' >> .gitignore

# 3. Используйте Docker secrets (Swarm)
# или переменные окружения в CI/CD

# 4. Регулярно обновляйте образы
docker-compose pull
docker-compose up -d --build
```

---

## Масштабирование

### Несколько экземпляров (не рекомендуется для Telegram bot)

Telegram bot API не поддерживает несколько экземпляров одного бота.
Каждый токен может использоваться только одним процессом.

Для масштабирования используйте:
- Более мощный сервер (вертикальное)
- Очереди сообщений для обработки (горизонтальное)

---

## Мониторинг

### Проверка здоровья

```bash
# Статус контейнера
docker-compose ps

# Использование ресурсов
docker stats youtube-transcript-bot

# Проверка логов на ошибки
docker-compose logs bot | grep -i error
```

### Метрики

Добавьте в docker-compose.yml:
```yaml
services:
  bot:
    # ... existing config
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=8000"
```

---

## Часто задаваемые вопросы

**Q: Можно ли использовать .env файл вместо переменных окружения?**
A: Нет, docker-compose.yml настроен на чтение переменных с хоста. Это безопаснее для production.

**Q: Как поменять порт?**
A: Бот не использует порты (только Telegram Bot API). Порты нужны только если добавите web-интерфейс.

**Q: Как использовать PostgreSQL вместо SQLite?**
A: Установите `YT_TRANSCRIPT_DATABASE_URL=postgresql://user:pass@host/db` и добавьте PostgreSQL контейнер в docker-compose.yml.

---

## Дополнительная информация

- **README.md** - Общая информация
- **DEPLOYMENT.md** - Другие варианты развертывания
- **CONTRIBUTING.md** - Разработка и тестирование
