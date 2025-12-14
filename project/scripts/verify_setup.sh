#!/bin/bash
ERRORS=0
# Проверка 1: Gunicorn установлен
echo "1. Проверка Gunicorn..."
if poetry run gunicorn --version &> /dev/null; then
    echo "   [OK] Gunicorn установлен"
    poetry run gunicorn --version
else
    echo "   [ERROR] Gunicorn не установлен"
    ((ERRORS++))
fi
echo ""

# Проверка 2: Конфигурация Gunicorn
echo "2. Проверка конфигурации Gunicorn..."
if [ -f "gunicorn.conf.py" ]; then
    echo "   [OK] gunicorn.conf.py существует"
    WORKERS=$(grep "^workers" gunicorn.conf.py | grep -oE "[0-9]+" || echo "0")
    if [ "$WORKERS" = "2" ]; then
        echo "   [OK] Количество воркеров: 2"
    else
        echo "   [WARN] Количество воркеров: $WORKERS (ожидается 2)"
    fi
else
    echo "   [ERROR] gunicorn.conf.py не найден"
    ((ERRORS++))
fi
echo ""

# Проверка 3: Простой WSGI скрипт
echo "3. Проверка простого WSGI скрипта..."
if [ -f "simple_wsgi.py" ]; then
    echo "   [OK] simple_wsgi.py существует"
    if poetry run python -c "from simple_wsgi import application; print('OK')" &> /dev/null; then
        echo "   [OK] WSGI приложение загружается корректно"
    else
        echo "   [ERROR] Ошибка загрузки WSGI приложения"
        ((ERRORS++))
    fi
else
    echo "   [ERROR] simple_wsgi.py не найден"
    ((ERRORS++))
fi
echo ""

# Проверка 4: Конфигурация Nginx
echo "4. Проверка конфигурации Nginx..."
if [ -f "nginx/askpupkin.conf" ]; then
    echo "   [OK] nginx/askpupkin.conf существует"
    LINES=$(wc -l < nginx/askpupkin.conf | tr -d ' ')
    echo "   Размер конфигурации: $LINES строк"
    if [ "$LINES" -le 50 ]; then
        echo "   [OK] Размер конфигурации <= 50 строк"
    else
        echo "   [WARN] Размер конфигурации > 50 строк ($LINES)"
    fi
    
    # Проверка наличия ключевых элементов
    if grep -q "upstream gunicorn_backend" nginx/askpupkin.conf; then
        echo "   [OK] Upstream настроен"
    else
        echo "   [ERROR] Upstream не найден"
        ((ERRORS++))
    fi
    
    if grep -q "proxy_cache" nginx/askpupkin.conf; then
        echo "   [OK] Proxy cache настроен"
    else
        echo "   [ERROR] Proxy cache не найден"
        ((ERRORS++))
    fi
    
    if grep -q "location /uploads/" nginx/askpupkin.conf; then
        echo "   [OK] Локация /uploads/ настроена"
    else
        echo "   [ERROR] Локация /uploads/ не найдена"
        ((ERRORS++))
    fi
    
    if grep -q "gzip on" nginx/askpupkin.conf; then
        echo "   [OK] Сжатие (gzip) настроено"
    else
        echo "   [ERROR] Сжатие не настроено"
        ((ERRORS++))
    fi
else
    echo "   [ERROR] nginx/askpupkin.conf не найден"
    ((ERRORS++))
fi
echo ""

# Проверка 5: Тестовый файл
echo "5. Проверка тестового файла..."
if [ -f "static/sample.html" ]; then
    echo "   [OK] static/sample.html существует"
else
    echo "   [ERROR] static/sample.html не найден"
    ((ERRORS++))
fi
echo ""

# Проверка 6: Скрипты
echo "6. Проверка скриптов..."
SCRIPTS=("start_gunicorn.sh" "start_simple_wsgi.sh" "test_nginx.sh" "benchmark.sh")
for script in "${SCRIPTS[@]}"; do
    if [ -f "scripts/$script" ]; then
        if [ -x "scripts/$script" ]; then
            echo "   [OK] scripts/$script (исполняемый)"
        else
            echo "   [WARN] scripts/$script (не исполняемый)"
        fi
    else
        echo "   [ERROR] scripts/$script не найден"
        ((ERRORS++))
    fi
done
echo ""

# Проверка 7: Отчет
echo "7. Проверка отчета..."
if [ -f "performance_report.md" ]; then
    echo "   [OK] performance_report.md существует"
else
    echo "   [WARN] performance_report.md не найден (создайте после тестирования)"
fi
echo ""

# Итоги
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "[OK] Все проверки пройдены!"
    echo "ДЗ6 готово к использованию."
else
    echo "[ERROR] Найдено ошибок: $ERRORS"
    echo "Исправьте ошибки перед использованием."
fi
echo "=========================================="

exit $ERRORS
