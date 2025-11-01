"""
URL configuration for askpupkin project.
"""

from django.contrib import admin
from django.urls import path, include

from app.handlers import handler404, handler500

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
]

# Обработчики ошибок
handler404 = handler404
handler500 = handler500
