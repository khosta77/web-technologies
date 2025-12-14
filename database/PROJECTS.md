# Инструкции по работе с базой данных

## Быстрый старт

```bash
make up-database
```

При первом запуске система запросит порт для контейнера и другие параметры БД.

## Работа с Docker

### Команды Makefile

```bash
make up-database        # Запустить PostgreSQL
make down-database      # Остановить и удалить контейнер
make stop-database      # Остановить контейнер (данные сохраняются)
make restart-database   # Перезапустить контейнер
make logs-database      # Показать логи
make status-database    # Показать статус контейнера
make shell-database     # Подключиться к БД через psql
make clean-database     # Удалить контейнер, данные и переменные БД из .env
make help               # Показать все команды
```

## Переменные окружения

### DOCKER_DB_PORT (для контейнера)
- Если указан → Django подключается к контейнеру на этом порту
- Если не указан → Django подключается к локальной PostgreSQL на порту 5432

### Остальные переменные (опционально)
- `DB_NAME` - имя базы данных (по умолчанию `askpupkin`)
- `DB_USER` - пользователь БД (по умолчанию `postgres` для контейнера, текущий пользователь для локальной БД)
- `DB_PASSWORD` - пароль БД (по умолчанию `postgres` для контейнера, пустой для локальной БД)
- `DB_HOST` - хост БД (по умолчанию `localhost`)

Все переменные автоматически запрашиваются при первом запуске `make up-database` и сохраняются в `.env`.

## Переключение между контейнером и локальной БД

- **Использовать контейнер:** Убедитесь, что `DOCKER_DB_PORT` указан в `.env`
- **Использовать локальную БД:** Удалите или закомментируйте `DOCKER_DB_PORT` в `.env`

## Полезные команды

### Миграции
```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py showmigrations
```

### Наполнение данными
```bash
poetry run python manage.py fill_db 10
```

### Подключение к БД
```bash
make shell-database
# или
docker compose exec postgres psql -U postgres -d askpupkin
```

### Резервное копирование
```bash
# Создать бэкап
docker compose exec postgres pg_dump -U postgres askpupkin > backup.sql

# Восстановить
docker compose exec -T postgres psql -U postgres askpupkin < backup.sql
```

## Решение проблем

### Контейнер не запускается
```bash
make logs-database  # Проверить логи
make status-database # Проверить статус
```

### Ошибка подключения
1. Проверьте, что контейнер запущен: `make status-database`
2. Проверьте переменные в `.env`
3. Убедитесь, что порт не занят: `lsof -i :5433`

### Полная очистка
```bash
make clean-database  # Удалит контейнер, данные и переменные БД из .env
```
