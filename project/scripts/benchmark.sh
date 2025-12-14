#!/bin/bash
# Скрипт для нагрузочного тестирования с помощью ab (Apache Benchmark)

REQUESTS=1000
CONCURRENCY=10
OUTPUT_DIR="$(dirname "$0")/../benchmark_results"
mkdir -p "$OUTPUT_DIR"

echo "Нагрузочное тестирование"
echo "Запросов: $REQUESTS"
echo "Параллельных соединений: $CONCURRENCY"
echo "Результаты сохраняются в: $OUTPUT_DIR"
echo ""

# Проверка наличия ab
if ! command -v ab &> /dev/null; then
    echo "[ERROR] Apache Benchmark (ab) не установлен!"
    echo "Установите: sudo apt-get install apache2-utils (Ubuntu/Debian)"
    echo "            brew install httpd (macOS)"
    exit 1
fi

# Тест 1: Статический документ напрямую через nginx
echo "=========================================="
echo "Тест 1: Статический документ через Nginx"
echo "=========================================="
ab -n $REQUESTS -c $CONCURRENCY http://localhost/sample.html > "$OUTPUT_DIR/1_static_nginx.txt" 2>&1
echo "Результаты сохранены в: $OUTPUT_DIR/1_static_nginx.txt"
echo ""

# Тест 2: Статический документ напрямую через gunicorn
echo "=========================================="
echo "Тест 2: Статический документ через Gunicorn"
echo "=========================================="
ab -n $REQUESTS -c $CONCURRENCY http://127.0.0.1:8000/static/sample.html > "$OUTPUT_DIR/2_static_gunicorn.txt" 2>&1
echo "Результаты сохранены в: $OUTPUT_DIR/2_static_gunicorn.txt"
echo ""

# Тест 3: Динамический документ напрямую через gunicorn
echo "=========================================="
echo "Тест 3: Динамический документ через Gunicorn"
echo "=========================================="
ab -n $REQUESTS -c $CONCURRENCY http://127.0.0.1:8000/ > "$OUTPUT_DIR/3_dynamic_gunicorn.txt" 2>&1
echo "Результаты сохранены в: $OUTPUT_DIR/3_dynamic_gunicorn.txt"
echo ""

# Тест 4: Динамический документ через nginx с проксированием (без кэша)
echo "=========================================="
echo "Тест 4: Динамический документ через Nginx (без кэша)"
echo "=========================================="
# Очищаем кэш перед тестом
rm -rf /tmp/nginx_cache/*
ab -n $REQUESTS -c $CONCURRENCY http://localhost/ > "$OUTPUT_DIR/4_dynamic_nginx_no_cache.txt" 2>&1
echo "Результаты сохранены в: $OUTPUT_DIR/4_dynamic_nginx_no_cache.txt"
echo ""

# Тест 5: Динамический документ через nginx с проксированием (с кэшем)
echo "=========================================="
echo "Тест 5: Динамический документ через Nginx (с кэшем)"
echo "=========================================="
# Первый запрос для заполнения кэша
curl -s http://localhost/ > /dev/null
sleep 1
ab -n $REQUESTS -c $CONCURRENCY http://localhost/ > "$OUTPUT_DIR/5_dynamic_nginx_with_cache.txt" 2>&1
echo "Результаты сохранены в: $OUTPUT_DIR/5_dynamic_nginx_with_cache.txt"
echo ""

echo "=========================================="
echo "[OK] Все тесты завершены!"
echo "=========================================="
echo "Результаты находятся в: $OUTPUT_DIR"
echo ""
echo "Для просмотра результатов используйте:"
echo "  cat $OUTPUT_DIR/*.txt"
