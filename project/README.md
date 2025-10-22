# AskPupkin 

## Структура проекта

```
project/
├── askpupkin/           # Django проект
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/           # Django шаблоны
│   ├── base.html       # Базовый шаблон
│   ├── index.html      # Главная страница
│   ├── question.html   # Страница вопроса
│   ├── ask.html        # Форма добавления вопроса
│   ├── login.html      # Форма авторизации
│   ├── signup.html     # Форма регистрации
│   ├── settings.html   # Страница настроек
│   └── tags.html       # Страница тегов
├── static/
│   ├── css/
│   │   ├── base.css        # Базовые стили и адаптивность
│   │   ├── layout.css      # Шапка, подвал, основная структура
│   │   ├── components.css  # Переиспользуемые компоненты
│   │   └── pages.css       # Стили для конкретных страниц
│   └── img/
│       └── avatar.jpg
└── manage.py
```

## Запуск Django сервера

```bash
cd project
source venv/bin/activate
python manage.py runserver 8000
```

* В браузере: `http://localhost:8000/`

## Установка зависимостей

```bash
cd project
python3 -m venv venv
source venv/bin/activate
pip install django
python manage.py migrate
```