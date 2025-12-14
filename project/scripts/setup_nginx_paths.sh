#!/bin/bash
# Скрипт для автоматической замены путей в конфигурации Nginx

NGINX_CONF="$(dirname "$0")/../nginx/askpupkin.conf"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Настройка путей в конфигурации Nginx..."
echo "Проект: $PROJECT_DIR"
echo ""

# Создаем резервную копию
cp "$NGINX_CONF" "$NGINX_CONF.bak"

# Заменяем пути
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|/path/to/project|$PROJECT_DIR|g" "$NGINX_CONF"
else
    # Linux
    sed -i "s|/path/to/project|$PROJECT_DIR|g" "$NGINX_CONF"
fi

echo "[OK] Пути обновлены в конфигурации Nginx"
echo "Резервная копия сохранена: $NGINX_CONF.bak"
echo ""
echo "Теперь можно проверить конфигурацию:"
echo "  ./scripts/test_nginx.sh"
