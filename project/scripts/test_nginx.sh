#!/bin/bash
# Скрипт для проверки конфигурации Nginx

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NGINX_CONF="$SCRIPT_DIR/../nginx/askpupkin.conf"
NGINX_CONF="$(cd "$(dirname "$NGINX_CONF")" && pwd)/$(basename "$NGINX_CONF")"

echo "Проверка конфигурации Nginx..."
echo "Файл: $NGINX_CONF"
echo ""

# Проверка синтаксиса
if command -v nginx &> /dev/null; then
    if nginx -t -c "$NGINX_CONF" 2>&1; then
        echo ""
        echo "[OK] Конфигурация Nginx корректна!"
        echo ""
        echo "Для запуска Nginx используйте:"
        echo "  sudo nginx -c $NGINX_CONF"
        echo ""
        echo "Для остановки:"
        echo "  sudo nginx -s stop"
    else
        echo ""
        echo "[ERROR] Ошибка в конфигурации Nginx!"
        exit 1
    fi
else
    echo "[WARN] Nginx не установлен или не найден в PATH"
    echo "Установите nginx для проверки конфигурации"
    exit 1
fi
