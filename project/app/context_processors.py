"""
Context processors для Django
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from django.http import HttpRequest


def user_context(request: HttpRequest) -> dict[str, Any]:
    """Добавляет текущего пользователя в контекст всех шаблонов"""
    # Используем встроенную систему авторизации Django
    user = request.user if request.user.is_authenticated else None

    path = request.path
    skip_best_members = (
        path in ["/login/", "/signup/", "/register/"]
        or path.startswith(("/admin/", "/__debug__/"))  # Django Debug Toolbar
    )

    if skip_best_members:
        best_members = []
    else:
        best_members = list(
            User.objects.select_related("profile", "profile__avatar")
            .filter(profile__isnull=False)
            .order_by("-profile__rating", "-id")[:5]
        )

    return {"user": user, "best_members": best_members}
