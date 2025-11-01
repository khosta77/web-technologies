"""
Context processors для Django
"""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest


def user_context(request: HttpRequest) -> dict[str, Any]:
    """Добавляет текущего пользователя в контекст всех шаблонов"""
    from .mockRepositories.user_mock_repository import UserMockRepository

    # Создаем экземпляр репозитория для получения пользователя
    repo = UserMockRepository()

    user_id = request.session.get("user_id")
    user = None
    if user_id:
        user = repo.get_user_by_id(user_id)

    # Получаем лучших пользователей
    best_members = repo.get_best_members(limit=5)

    return {"user": user, "best_members": best_members}
