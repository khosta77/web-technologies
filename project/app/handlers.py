"""
Обработчики ошибок для Django
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def handler404(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Обработчик ошибки 404"""
    return render(request, "404.html", status=404)


def handler500(request: HttpRequest) -> HttpResponse:
    """Обработчик ошибки 500"""
    return render(request, "500.html", status=500)
