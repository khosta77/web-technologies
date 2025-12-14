#!/bin/bash
# Скрипт для запуска простого WSGI приложения на порту 8081

cd "$(dirname "$0")/.." || exit 1

echo "Запуск простого WSGI приложения..."
echo "Порт: 8081"
echo "Адрес: http://localhost:8081"
echo ""

poetry run gunicorn --bind 0.0.0.0:8081 --workers 2 simple_wsgi:application
