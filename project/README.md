# AskPupkin 

Django-приложение для вопросов и ответов по аналогии со Stack Overflow

## Структура проекта

```
project/
├── app/                      # Django приложение
│   ├── interfaces/          # Интерфейсы (абстракции)
│   │   ├── question_interface.py
│   │   ├── answer_interface.py
│   │   ├── tag_interface.py
│   │   └── user_interface.py
│   ├── mockRepositories/    # Mock репозитории (заглушки для тестов)
│   │   ├── question_mock_repository.py
│   │   ├── answer_mock_repository.py
│   │   ├── tag_mock_repository.py
│   │   ├── user_mock_repository.py
│   │   └── mock_data_frames.py    # Данные-заглушки
│   ├── repositories/        # Репозитории Django ORM
│   │   ├── question_repository.py
│   │   ├── answer_repository.py
│   │   ├── tag_repository.py
│   │   └── user_repository.py
│   ├── constants.py          # Константы приложения
│   ├── utils.py             # Утилиты (пагинация)
│   ├── views.py             # View функции
│   ├── urls.py              # URL маршруты
│   ├── models.py            # Django модели
│   ├── admin.py             # Админ-панель
│   ├── signals.py           # Django сигналы
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
│   │   ├── search.js          # Поиск
│   │   └── dropdown.js        # Выпадающее меню пользователя
│   └── img/
│       ├── avatar.jpg
│       ├── logo.png
│       └── search.jpg
├── uploads/                # Файлы, загруженные пользователями
│   └── img/
│       └── avatar.jpg      # Дефолтный аватар
├── db.sqlite3              # База данных
├── manage.py
└── README.md
```

## Архитектура

### Интерфейсы (app/interfaces/)
Абстрактные классы для работы с данными:
- `IQuestionRepository` - интерфейс для работы с вопросами
- `IAnswerRepository` - интерфейс для работы с ответами  
- `ITagRepository` - интерфейс для работы с тегами

### Mock репозитории (app/mockRepositories/)
Реализация интерфейсов с заглушками для тестирования (используются в тестах):
- `QuestionMockRepository` - вопросы с данными из `mock_data_frames.py`
- `AnswerMockRepository` - ответы
- `TagMockRepository` - теги
- `UserMockRepository` - пользователи
- `mock_data_frames.py` - реалистичные данные для тестирования

### Репозитории (app/repositories/)
Реализация интерфейсов с использованием Django ORM (используются в views и основном коде):
- `QuestionRepository` - вопросы через Django ORM
- `AnswerRepository` - ответы через Django ORM
- `TagRepository` - теги через Django ORM
- `UserRepository` - пользователи через Django ORM

Все views используют репозитории через интерфейсы, что обеспечивает абстракцию от конкретной реализации (Django ORM или mock-данные).

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

```bash
cd project
poetry install
poetry run python manage.py runserver 8000
```

* В браузере: `http://localhost:8000/`

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
poetry run python manage.py fill_db 100 # Стандартный набор данных
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

---

Важно, перед каждым запуском проводить:

```bash
poetry run poe ci
```