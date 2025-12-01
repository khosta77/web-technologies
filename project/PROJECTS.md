# Инструкции по работе с базой данных

Этот документ описывает настройку и работу с PostgreSQL базой данных в Docker контейнере для проекта AskPupkin.

## Быстрый старт

1. **Настройте переменные окружения (опционально):**
   ```bash
   cd project
   cp .env.example .env
   # Отредактируйте .env и установите SECRET_KEY и DB_PASSWORD при необходимости
   ```

2. **Запустите базу данных:**
   ```bash
   make up-database
   ```

3. **Выполните миграции и запустите сервер:**
   ```bash
   poetry run python manage.py migrate
   poetry run python manage.py runserver 8000
   ```

4. **Откройте в браузере:**
   ```
   http://localhost:8000/
   ```

---

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Настройка окружения](#настройка-окружения)
- [Работа с Docker](#работа-с-docker)
- [Миграции базы данных](#миграции-базы-данных)
- [Наполнение данными](#наполнение-данными)
- [Полезные команды](#полезные-команды)
- [Резервное копирование](#резервное-копирование)
- [Решение проблем](#решение-проблем)

## Быстрый старт

### 1. Установка Docker

Убедитесь, что у вас установлен Docker и Docker Compose:

```bash
# Проверка установки Docker
docker --version

# Проверка установки Docker Compose
# Вариант 1: Docker Compose V2 (плагин, рекомендуется)
docker compose version

# Вариант 2: Docker Compose V1 (отдельная утилита)
docker-compose --version
```

**Примечание:** В проекте используются команды `docker-compose`, но если у вас установлен Docker Compose V2 (плагин), используйте `docker compose` (без дефиса) вместо `docker-compose`.

```bash
brew install docker-compose
```

### 2. Настройка переменных окружения (опционально)

Для быстрого старта можно использовать значения по умолчанию из `docker-compose.yml`. Если нужно настроить кастомные значения:

```bash
cd project
cp .env.example .env
# Отредактируйте .env и установите нужные значения
```

**Минимальные настройки для безопасности:**
- `SECRET_KEY` - секретный ключ Django (обязательно измените в production!)
- `DB_PASSWORD` - пароль базы данных (рекомендуется изменить)

Остальные параметры можно оставить по умолчанию.

### 3. Запуск базы данных

Используйте Makefile для управления контейнером:

```bash
make up-database    # Запустить PostgreSQL
```

Или напрямую через docker-compose:

```bash
docker-compose up -d postgres
# или
docker compose up -d postgres
```

### 4. Выполнение миграций

После запуска контейнера выполните миграции Django:

```bash
poetry run python manage.py migrate
```

### 5. Запуск сервера

```bash
poetry run python manage.py runserver 8000
```

### 6. (Опционально) Наполнение тестовыми данными

После запуска сервера, в другом терминале выполните:

```bash
poetry run python manage.py fill_db 10
```

Где `10` - коэффициент масштабирования (создаст 10 пользователей, 100 вопросов и т.д.)

## Настройка окружения

### Переменные окружения

Проект использует следующие переменные окружения для настройки БД:

| Переменная | Описание | Значение по умолчанию |
|------------|-----------|----------------------|
| `DB_NAME` | Имя базы данных | `askpupkin` |
| `DB_USER` | Пользователь БД | `postgres` |
| `DB_PASSWORD` | Пароль БД | `postgres` |
| `DB_HOST` | Хост БД | `localhost` (автоматически `postgres` в Docker) |
| `DB_PORT` | Порт БД | `5432` |
| `USE_SQLITE` | Использовать SQLite вместо PostgreSQL | `false` |

### Автоматическое определение Docker

Проект автоматически определяет, запущен ли он в Docker контейнере:
- Если приложение запущено в Docker, используется хост `postgres` (имя сервиса)
- Если приложение запущено локально, используется хост `localhost`

Вы можете явно указать хост через переменную `DB_HOST`.

## Работа с Docker

### Использование Makefile (рекомендуется)

Для удобства используйте команды Makefile:

```bash
make up-database        # Запустить PostgreSQL
make down-database      # Остановить и удалить контейнер
make stop-database      # Остановить контейнер (данные сохраняются)
make restart-database   # Перезапустить контейнер
make logs-database      # Показать логи в реальном времени
make status-database     # Показать статус контейнера
make shell-database      # Подключиться к БД через psql
make clean-database      # Удалить контейнер и все данные (ОПАСНО!)
make help               # Показать все доступные команды
```

### Прямые команды Docker Compose

Если Makefile недоступен, используйте команды напрямую:

**Примечание:** В примерах используется `docker-compose`, но если у вас установлен Docker Compose V2 (плагин), замените на `docker compose` (без дефиса).

```bash
# Запуск в фоновом режиме
docker-compose up -d postgres

# Остановка без удаления данных
docker-compose stop postgres

# Остановка и удаление контейнера (данные сохраняются)
docker-compose down

# Удаление контейнера и всех данных
docker-compose down -v

# Просмотр логов
docker-compose logs -f postgres

# Статус контейнера
docker-compose ps
```

## Миграции базы данных

### Создание миграций

```bash
# Создать миграции для всех изменений моделей
poetry run python manage.py makemigrations

# Создать миграции для конкретного приложения
poetry run python manage.py makemigrations app
```

### Применение миграций

```bash
# Применить все миграции
poetry run python manage.py migrate

# Применить миграции для конкретного приложения
poetry run python manage.py migrate app

# Показать статус миграций
poetry run python manage.py showmigrations
```

### Откат миграций

```bash
# Откатить последнюю миграцию
poetry run python manage.py migrate app <номер_предыдущей_миграции>

# Например, откатить до 0001_initial
poetry run python manage.py migrate app 0001_initial
```

## Наполнение данными

### Использование команды fill_db

```bash
# Базовое наполнение (ratio=100)
poetry run python manage.py fill_db

# Кастомный коэффициент
poetry run python manage.py fill_db 50

# Что создается:
# - ratio пользователей
# - ratio * 10 вопросов
# - ratio * 100 ответов
# - ratio тегов
# - ratio * 200 оценок (лайков)
```

### Подключение к БД напрямую

```bash
# Через docker-compose
docker-compose exec postgres psql -U postgres -d askpupkin

# Или через docker напрямую
docker exec -it askpupkin_postgres psql -U postgres -d askpupkin
```

### Полезные SQL команды

```sql
-- Показать все таблицы
\dt

-- Показать структуру таблицы
\d app_question

-- Подсчет записей
SELECT COUNT(*) FROM app_question;
SELECT COUNT(*) FROM app_answer;
SELECT COUNT(*) FROM auth_user;

-- Выход
\q
```

## Полезные команды

### Управление контейнером

```bash
# Перезапуск контейнера
docker-compose restart postgres

# Просмотр использования ресурсов
docker stats askpupkin_postgres

# Вход в контейнер
docker-compose exec postgres sh
```

### Работа с данными

```bash
# Создать суперпользователя Django
poetry run python manage.py createsuperuser

# Очистить все данные (удалить и пересоздать БД)
docker-compose down -v
docker-compose up -d postgres
poetry run python manage.py migrate
```

## Резервное копирование

### Создание бэкапа

```bash
# Создать бэкап
docker-compose exec postgres pg_dump -U postgres askpupkin > backup_$(date +%Y%m%d_%H%M%S).sql

# Создать бэкап с сжатием
docker-compose exec postgres pg_dump -U postgres -Fc askpupkin > backup_$(date +%Y%m%d_%H%M%S).dump
```

### Восстановление из бэкапа

```bash
# Восстановить из SQL файла
docker-compose exec -T postgres psql -U postgres askpupkin < backup_20240101_120000.sql

# Восстановить из сжатого дампа
docker-compose exec -T postgres pg_restore -U postgres -d askpupkin < backup_20240101_120000.dump
```

### Автоматическое резервное копирование

Для production рекомендуется настроить автоматические бэкапы через cron:

```bash
# Добавить в crontab (crontab -e)
0 2 * * * cd /path/to/project && docker-compose exec -T postgres pg_dump -U postgres askpupkin > /backups/askpupkin_$(date +\%Y\%m\%d).sql
```

## Решение проблем

### Контейнер не запускается

1. Проверьте логи:
   ```bash
   docker-compose logs postgres
   ```

2. Проверьте, не занят ли порт 5432:
   ```bash
   lsof -i :5432  # macOS/Linux
   netstat -ano | findstr :5432  # Windows
   ```

3. Измените порт в `.env`:
   ```bash
   DB_PORT=5433
   ```

### Ошибка подключения к БД

1. Убедитесь, что контейнер запущен:
   ```bash
   docker-compose ps
   ```

2. Проверьте переменные окружения в `.env`

3. Проверьте подключение:
   ```bash
   docker-compose exec postgres pg_isready -U postgres
   ```

### Ошибка "database does not exist"

Создайте базу данных вручную:

```bash
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE askpupkin;"
```

### Ошибка "password authentication failed"

Проверьте пароль в `.env` и перезапустите контейнер:

```bash
docker-compose down
docker-compose up -d postgres
```

### Данные не сохраняются

Убедитесь, что volume создан:

```bash
docker volume ls | grep postgres_data
```

Если volume отсутствует, пересоздайте контейнер:

```bash
docker-compose down -v
docker-compose up -d postgres
```

### Очистка и перезапуск с нуля

Если нужно полностью начать заново:

```bash
# Остановить и удалить контейнер с данными
docker-compose down -v

# Запустить заново
docker-compose up -d postgres

# Подождать несколько секунд для инициализации
sleep 5

# Выполнить миграции
poetry run python manage.py migrate

# Создать суперпользователя (опционально)
poetry run python manage.py createsuperuser

# Наполнить тестовыми данными (опционально)
poetry run python manage.py fill_db 10
```

## Production рекомендации

Для production окружения рекомендуется:

1. **Использовать managed БД** (AWS RDS, Google Cloud SQL, Azure Database)
2. **Настроить автоматические бэкапы** с хранением в отдельном хранилище
3. **Использовать секреты** вместо `.env` файлов (Docker secrets, Kubernetes secrets)
4. **Настроить мониторинг** (Prometheus, Grafana)
5. **Использовать connection pooling** (PgBouncer)
6. **Настроить read replicas** для масштабирования чтения
7. **Регулярно обновлять** образ PostgreSQL

## Дополнительные ресурсы

- [Docker Compose документация](https://docs.docker.com/compose/)
- [PostgreSQL документация](https://www.postgresql.org/docs/)
- [Django database документация](https://docs.djangoproject.com/en/stable/topics/db/)

