"""
Простой WSGI скрипт без использования Django

Выводит список переданных GET и POST параметров.
Запускается на порту 8081.

Использование:
    gunicorn --bind 0.0.0.0:8081 simple_wsgi:application
"""

from urllib.parse import parse_qs


def application(environ, start_response):
    """
    WSGI приложение для вывода GET и POST параметров

    Args:
        environ: Словарь переменных окружения WSGI
        start_response: Callback функция для начала ответа

    Returns:
        Итератор с телом ответа
    """
    # Получаем метод запроса
    method = environ.get("REQUEST_METHOD", "GET")

    # Получаем GET параметры из QUERY_STRING
    get_params = {}
    query_string = environ.get("QUERY_STRING", "")
    if query_string:
        get_params = parse_qs(query_string)

    # Получаем POST параметры из wsgi.input
    post_params = {}
    if method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
            if content_length > 0:
                post_data = environ["wsgi.input"].read(content_length).decode("utf-8")
                post_params = parse_qs(post_data)
        except (ValueError, KeyError):
            pass

    # Формируем HTML ответ
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WSGI Parameters</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
        }
        .section {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .param {
            margin: 10px 0;
            padding: 10px;
            background: #f9f9f9;
            border-left: 3px solid #4CAF50;
        }
        .method {
            display: inline-block;
            padding: 5px 10px;
            background: #2196F3;
            color: white;
            border-radius: 3px;
            font-weight: bold;
        }
        .empty {
            color: #999;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>WSGI Parameters Viewer</h1>
    
    <div class="section">
        <h2>Request Method: <span class="method">{method}</span></h2>
    </div>
    
    <div class="section">
        <h2>GET Parameters:</h2>
        {get_params_html}
    </div>
    
    <div class="section">
        <h2>POST Parameters:</h2>
        {post_params_html}
    </div>
    
    <div class="section">
        <h2>Request Info:</h2>
        <p><strong>Path:</strong> {path}</p>
        <p><strong>Server:</strong> {server}</p>
        <p><strong>Port:</strong> 8081</p>
    </div>
</body>
</html>"""

    # Форматируем GET параметры
    if get_params:
        get_params_html = "".join(
            f'<div class="param"><strong>{key}:</strong> {", ".join(values)}</div>'
            for key, values in get_params.items()
        )
    else:
        get_params_html = '<div class="empty">Нет GET параметров</div>'

    # Форматируем POST параметры
    if post_params:
        post_params_html = "".join(
            f'<div class="param"><strong>{key}:</strong> {", ".join(values)}</div>'
            for key, values in post_params.items()
        )
    else:
        post_params_html = '<div class="empty">Нет POST параметров</div>'

    # Заполняем шаблон
    response_body = html.format(
        method=method,
        get_params_html=get_params_html,
        post_params_html=post_params_html,
        path=environ.get("PATH_INFO", "/"),
        server=environ.get("SERVER_NAME", "localhost"),
    )

    # Устанавливаем заголовки ответа
    status = "200 OK"
    headers = [("Content-Type", "text/html; charset=utf-8")]

    start_response(status, headers)

    # Возвращаем тело ответа
    return [response_body.encode("utf-8")]
