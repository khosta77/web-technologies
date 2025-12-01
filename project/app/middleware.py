"""
Middleware для обработки 404 и 500 ошибок
"""

from __future__ import annotations

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin


class CustomErrorMiddleware(MiddlewareMixin):
    """Middleware для показа кастомных страниц 404 и 500 даже при DEBUG = True"""

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Обрабатывает ответ и показывает кастомную 404 если статус 404
        """
        # Исключаем админку из обработки ошибок
        if request.path.startswith("/admin/"):
            return response

        if response.status_code == 404:
            try:
                # Добавляем user в контекст через context processor
                from app.context_processors import user_context

                context = user_context(request)
                return render(request, "404.html", context, status=404)
            except Exception:
                # Если что-то пошло не так, возвращаем стандартную страницу
                pass

        return response

    def process_exception(self, request: HttpRequest, exception: Exception) -> HttpResponse | None:
        """
        Обрабатывает исключения и показывает кастомную страницу 500
        даже при DEBUG = True
        """
        # Исключаем админку из обработки ошибок
        if request.path.startswith("/admin/"):
            return None

        # Http404 обрабатывается через process_response
        if isinstance(exception, Http404):
            return None

        try:
            # Добавляем user в контекст через context processor
            from app.context_processors import user_context

            context = user_context(request)
            return render(request, "500.html", context, status=500)
        except Exception:
            # Если что-то пошло не так при рендеринге страницы ошибки,
            # возвращаем None, чтобы Django обработал исключение стандартным способом
            return None
