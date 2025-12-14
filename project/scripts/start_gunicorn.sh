#!/bin/bash
# Скрипт для запуска Gunicorn с Django приложением

cd "$(dirname "$0")/.." || exit 1

echo "Запуск Gunicorn для Django приложения askpupkin..."
echo "Конфигурация: gunicorn.conf.py"
echo "Воркеров: 2"
echo "Адрес: http://127.0.0.1:8000"
echo ""

poetry run gunicorn -c gunicorn.conf.py askpupkin.wsgi:application
