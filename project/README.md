# AskPupkin 

Django-приложение для вопросов и ответов по аналогии со Stack Overflow

## Структура проекта

```
project/
├── app/                      # Django приложение
│   ├── interfaces/          # Интерфейсы (абстракции)
│   │   ├── question_interface.py
│   │   ├── answer_interface.py
│   │   └── tag_interface.py
│   ├── mockRepositories/    # Mock репозитории (заглушки для тестов)
│   │   ├── question_mock_repository.py
│   │   ├── answer_mock_repository.py
│   │   ├── tag_mock_repository.py
│   │   └── mock_data_frames.py    # Данные-заглушки
│   ├── constants.py          # Константы приложения
│   ├── utils.py             # Утилиты (пагинация)
│   ├── views.py             # View функции
│   ├── urls.py              # URL маршруты
│   └── models.py            # Модели (пока пустой)
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
│   └── tags.html          # Страница тегов
├── static/
│   ├── css/
│   │   ├── base.css       # Базовые стили и адаптивность
│   │   ├── layout.css     # Шапка, подвал, основная структура
│   │   ├── components.css # Переиспользуемые компоненты
│   │   └── pages.css      # Стили для конкретных страниц
│   ├── js/
│   │   ├── validation.js      # Валидация регистрации
│   │   ├── login-validation.js # Валидация входа
│   │   └── search.js          # Поиск
│   └── img/
│       ├── avatar.jpg
│       ├── logo.png
│       └── search.jpg
├── db.sqlite3              # База данных (SQLite)
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
Реализация интерфейсов с заглушками для тестирования:
- `QuestionMockRepository` - вопросы с данными из `mock_data_frames.py`
- `AnswerMockRepository` - ответы
- `TagMockRepository` - теги
- `mock_data_frames.py` - реалистичные данные для тестирования

В будущем (ДЗ3) эти репозитории будут заменены на реальные, работающие с БД через Django ORM.

## Запуск Django сервера

### С Poetry

```bash
cd project
poetry install                    # Установка зависимостей
poetry run python manage.py runserver 8000
```

* В браузере: `http://localhost:8000/`

## Установка зависимостей

### С Poetry

```bash
poetry install
poetry run python manage.py migrate
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

## Технологии

- **Backend:** Django 5.2.7
- **Frontend:** HTML, CSS, JavaScript
