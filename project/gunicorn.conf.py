"""
Конфигурация Gunicorn для запуска Django приложения askpupkin

Использование:
    gunicorn -c gunicorn.conf.py askpupkin.wsgi:application
"""

import multiprocessing

# Количество воркеров
workers = 2

# Привязка к адресу и порту
bind = "127.0.0.1:8000"

# WSGI приложение
wsgi_app = "askpupkin.wsgi:application"

# Класс воркера
worker_class = "sync"

# Таймауты
timeout = 120
keepalive = 5

# Логирование
accesslog = "-"  # stdout
errorlog = "-"  # stderr
loglevel = "info"

# Перезапуск при изменении кода (для разработки)
reload = False

# Имя процесса
proc_name = "askpupkin"
