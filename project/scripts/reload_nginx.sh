#!/bin/bash
# Скрипт для перезагрузки nginx с правильной конфигурацией

NGINX_CONF="$(dirname "$0")/../nginx/askpupkin.conf"
NGINX_CONF_ABS="$(cd "$(dirname "$NGINX_CONF")" && pwd)/$(basename "$NGINX_CONF")"

echo "Остановка всех процессов nginx..."
sudo nginx -s stop 2>/dev/null || true
sudo pkill -9 nginx 2>/dev/null || true
sleep 1

echo "Проверка конфигурации..."
nginx -t -c "$NGINX_CONF_ABS" 2>&1

if [ $? -eq 0 ]; then
    echo "Запуск nginx с конфигурацией: $NGINX_CONF_ABS"
    sudo nginx -c "$NGINX_CONF_ABS"
    echo "[OK] Nginx запущен"
else
    echo "[ERROR] Ошибка в конфигурации!"
    exit 1
fi
