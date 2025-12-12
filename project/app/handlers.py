"""
Обработчики ошибок для Django
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from app.context_processors import user_context


def handler404(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Обработчик ошибки 404"""
    return render(request, "404.html", user_context(request), status=404)


def handler500(request: HttpRequest) -> HttpResponse:
    """Обработчик ошибки 500"""
    return render(request, "500.html", user_context(request), status=500)
