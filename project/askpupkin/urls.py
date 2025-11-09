"""
URL configuration for askpupkin project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

from app.handlers import handler404, handler500


def favicon_view(request):
    """Обработчик для favicon.ico - возвращает пустой ответ"""
    return HttpResponse(status=204)  # No Content

# Поддержка media файлов в режиме разработки (добавляем ПЕРВЫМИ)
urlpatterns = []
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Django Debug Toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]

# Основные URL паттерны
urlpatterns += [
    path("favicon.ico", favicon_view, name="favicon"),
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
]

# Обработчики ошибок
handler404 = handler404
handler500 = handler500
