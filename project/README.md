# AskPupkin 

Django-приложение для вопросов и ответов по аналогии со Stack Overflow

## Структура проекта

```
project/
├── app/                      # Django приложение
│   ├── mockRepositories/    # Mock репозитории (заглушки для тестов)
│   │   ├── user_mock_repository.py
│   │   └── mock_users.py    # Mock данные для пользователей
│   ├── repositories/        # Репозитории Django ORM
│   │   ├── question_repository.py
│   │   ├── answer_repository.py
│   │   ├── tag_repository.py
│   │   └── user_repository.py
│   ├── templatetags/        # Кастомные фильтры для шаблонов
│   │   ├── __init__.py
│   │   └── dict_filters.py  # Фильтр get_item для работы со словарями
│   ├── constants.py          # Константы приложения
│   ├── utils.py             # Утилиты (пагинация)
│   ├── avatar_utils.py      # Утилиты для работы с аватарами (дедупликация)
│   ├── views.py             # View функции (включая AJAX обработчики)
│   ├── urls.py              # URL маршруты (включая AJAX endpoints)
│   ├── models.py            # Django модели
│   ├── admin.py             # Админ-панель
│   ├── context_processors.py # Context processors
│   ├── handlers.py          # Обработчики ошибок (404, 500)
│   ├── middleware.py        # Custom middleware
│   ├── management/         # Management команды
│   │   └── commands/
│   │       └── fill_db.py   # Команда для наполнения БД
│   ├── migrations/          # Миграции БД
│   └── tests/               # Тесты
├── askpupkin/               # Конфигурация Django проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/               # Django шаблоны
│   ├── base.html           # Базовый шаблон (с правой колонкой)
│   ├── base_auth.html      # Базовый шаблон для авторизации
│   ├── index.html          # Главная страница (новые вопросы)
│   ├── question.html       # Страница вопроса
│   ├── paginator.html      # Шаблон пагинации
│   ├── ask.html            # Форма добавления вопроса
│   ├── login.html          # Форма авторизации
│   ├── signup.html         # Форма регистрации
│   ├── settings.html       # Страница настроек
│   ├── tags.html          # Страница тегов
│   ├── profile.html       # Страница профиля пользователя
│   ├── 404.html           # Страница 404
│   └── 500.html           # Страница 500
├── static/
│   ├── css/
│   │   ├── base.css       # Базовые стили и адаптивность
│   │   ├── layout.css     # Шапка, подвал, основная структура
│   │   ├── components.css # Переиспользуемые компоненты
│   │   └── pages.css      # Стили для конкретных страниц
│   ├── js/
│   │   ├── validation.js      # Валидация регистрации
│   │   ├── login-validation.js # Валидация входа
│   │   ├── signup-validation.js # Валидация регистрации
│   │   ├── search.js          # Поиск
│   │   ├── dropdown.js        # Выпадающее меню пользователя
│   │   ├── votes.js           # AJAX обработка лайков и отметки правильного ответа
│   │   └── settings.js         # Обработка формы настроек (превью аватара)
│   ├── img/
│   │   ├── avatar.jpg
│   │   ├── logo.png
│   │   └── search.jpg
│   └── sample.html         # Тестовый файл для проверки статики (ДЗ6)
├── uploads/                # Файлы, загруженные пользователями
│   └── avatars/
│       └── unique/         # Уникальные аватары (дедупликация по хешу)
├── gunicorn.conf.py        # Конфигурация Gunicorn (2 воркера)
├── simple_wsgi.py          # Простой WSGI скрипт без Django
├── nginx/                  # Конфигурация Nginx
│   └── askpupkin.conf      # Конфигурация Nginx (<50 строк)
├── scripts/                # Скрипты для ДЗ6
│   ├── start_gunicorn.sh   # Запуск Gunicorn для Django
│   ├── start_simple_wsgi.sh # Запуск простого WSGI (порт 8081)
│   ├── test_nginx.sh       # Проверка конфигурации Nginx
│   ├── setup_nginx_paths.sh # Автоматическая настройка путей
│   ├── benchmark.sh        # Нагрузочное тестирование
│   └── verify_setup.sh     # Проверка всех компонентов
├── performance_report.md   # Отчет о производительности (ДЗ6)
├── db.sqlite3              # База данных
├── manage.py
└── README.md
```

## Архитектура

### Mock репозитории (app/mockRepositories/)
Mock репозитории для тестирования:
- `UserMockRepository` - mock репозиторий для пользователей (используется в тестах)
- `mock_users.py` - mock данные для пользователей

### Репозитории (app/repositories/)
Репозитории для работы с данными через Django ORM (используются в views и основном коде):
- `QuestionRepository` - вопросы через Django ORM
- `AnswerRepository` - ответы через Django ORM
- `TagRepository` - теги через Django ORM
- `UserRepository` - пользователи через Django ORM

### Django модели (app/models.py)
Модели данных для работы с БД:
- `Profile` - профиль пользователя (расширение User, аватар, рейтинг)
- `Tag` - теги для вопросов
- `Question` - вопросы с кастомным менеджером (new, hot, by_tag)
- `Answer` - ответы на вопросы
- `QuestionLike` - лайки/дизлайки вопросов
- `AnswerLike` - лайки/дизлайки ответов

## Запуск Django сервера

### С Poetry

1. **Настройка переменных окружения для БД (один раз):**

   ```bash
   cp ../database/.env.example ../database/.env
   ```

2. **Запуск базы данных:**

   ```bash
   make -C ../database up-database
   ```

3. **Выполнение миграций и запуск сервера:**

   ```bash
   poetry install
   poetry run python manage.py migrate
   poetry run python manage.py runserver 8000
   ```

   * В браузере: `http://localhost:8000/`

**Подробные инструкции по работе с БД см. в [PROJECTS.md](PROJECTS.md)**

## Установка зависимостей

### С Poetry

```bash
poetry install
poetry run python manage.py migrate
```

## Настройка базы данных

Проект использует **PostgreSQL** по умолчанию для разработки и production.

Для заполнения БД тестовыми данными используйте команду:

```bash
poetry run python manage.py fill_db [ratio]
```

Где `ratio` - коэффициент масштабирования данных (по умолчанию 100):
- `ratio` пользователей
- `ratio * 10` вопросов
- `ratio * 100` ответов
- `ratio * 50` лайков вопросов
- `ratio * 150` лайков ответов

Пример:
```bash
poetry run python manage.py fill_db 100
```

## Инструменты качества кода

Проект использует Poetry для управления зависимостями и Poe the Poet для запуска задач.

### Установка зависимостей

```bash
poetry install
```

### Команды для проверок

```bash
poetry run poe ci
```

### Инструменты

- **pytest** — тестирование
- **ruff** — быстрый линтер и форматтер
- **mypy** — проверка типов
- **flake8** - проверки линтеров
- **bandit** — анализ безопасности кода
- **vulture** — поиск неиспользуемого кода

## Основные страницы

- `/` - Главная страница (новые вопросы)
- `/hot/` - Популярные вопросы
- `/question/<id>/` - Страница вопроса с ответами
- `/tag/<tag_name>/` - Вопросы по тегу
- `/tags/` - Все теги
- `/login/` - Авторизация
- `/register/` - Регистрация
- `/ask/` - Добавить вопрос
- `/settings/` - Настройки профиля
- `/profile/<user_id>/` - Профиль пользователя

## Модель данных

### Основные модели:

1. **Profile** - Профиль пользователя
   - Расширяет стандартную модель User
   - Содержит аватар (ImageField)
   - Метод `get_rating()` - вычисляет рейтинг пользователя

2. **Tag** - Теги для вопросов
   - Уникальное имя тега

3. **Question** - Вопросы
   - Кастомный менеджер с методами: `new()`, `hot()`, `by_tag()`
   - Связи с User (автор), Tag (many-to-many)
   - Метод `update_rating()` - обновляет рейтинг из лайков

4. **Answer** - Ответы на вопросы
   - Связи с User (автор), Question (вопрос)
   - Поле `is_correct` - правильный ответ
   - Метод `update_rating()` - обновляет рейтинг из лайков

5. **QuestionLike** - Оценки вопросов
   - Связи с User и Question
   - Значение: +1 (лайк) или -1 (дизлайк)
   - Автоматически обновляет рейтинг вопроса

6. **AnswerLike** - Оценки ответов
   - Связи с User и Answer
   - Значение: +1 (лайк) или -1 (дизлайк)
   - Автоматически обновляет рейтинг ответа

## Технологии

- **Backend:** Django 5.2.7
- **Frontend:** HTML, CSS, JavaScript
- **Database:** PostgreSQL
- **Dependency Management:** Poetry
- **Testing:** pytest, pytest-django
- **Code Quality:** ruff, mypy, flake8, bandit, vulture

## Домашнее задание 6: Настройка веб-серверов

### Быстрый старт

1. **Проверка настройки:**
   ```bash
   ./scripts/verify_setup.sh
   ```

2. **Запуск Gunicorn для Django:**
   ```bash
   ./scripts/start_gunicorn.sh
   # Приложение доступно: http://127.0.0.1:8000
   ```

3. **Запуск простого WSGI (опционально):**
   ```bash
   ./scripts/start_simple_wsgi.sh
   # Приложение доступно: http://localhost:8081
   # Проверка: http://localhost:8081?param1=value1&param2=value2
   ```

4. **Запуск Nginx:**
   ```bash
   ./scripts/test_nginx.sh  # Проверка конфигурации
   sudo nginx -c $(pwd)/nginx/askpupkin.conf  # Запуск
   # Проверка: http://localhost/sample.html
   ```

5. **Нагрузочное тестирование:**
   ```bash
   ./scripts/benchmark.sh
   # Результаты в benchmark_results/
   ```

### Конфигурация

**Gunicorn** (`gunicorn.conf.py`):
- Workers: 2
- Bind: 127.0.0.1:8000
- WSGI app: askpupkin.wsgi:application

**Nginx** (`nginx/askpupkin.conf`):
- Размер: 46 строк
- Upstream для Gunicorn
- Proxy cache настроен
- Статика: `/uploads/` и файлы по расширениям
- Сжатие (gzip)
- Кэширование браузера

**Простой WSGI** (`simple_wsgi.py`):
- Работает без Django
- Выводит GET и POST параметры
- Порт: 8081

### Нагрузочное тестирование

Скрипт `benchmark.sh` выполняет 5 тестов:
1. Статический документ через Nginx
2. Статический документ через Gunicorn
3. Динамический документ через Gunicorn
4. Динамический документ через Nginx (без кэша)
5. Динамический документ через Nginx (с кэшем)

Результаты сохраняются в `benchmark_results/`. Заполните `performance_report.md` результатами тестирования.

### Требования

- Gunicorn (установлен через `poetry add gunicorn`)
- Nginx (установите отдельно: `brew install nginx` или `sudo apt-get install nginx`)
- Apache Benchmark (для тестирования: `brew install httpd` или `sudo apt-get install apache2-utils`)

---

Важно, перед каждым запуском проводить:

```bash
poetry run poe ci
```