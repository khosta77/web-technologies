"""
Context processors для Django
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from django.http import HttpRequest

from .repositories import UserRepository


# Создаем экземпляр репозитория
user_repository = UserRepository()


def user_context(request: HttpRequest) -> dict[str, Any]:
    """Добавляет текущего пользователя в контекст всех шаблонов"""
    user_id = request.session.get("user_id")
    user = None
    if user_id:
        user = user_repository.get_user_by_id(user_id)

    # Получаем лучших пользователей по рейтингу через репозиторий
    best_members_dicts = user_repository.get_best_members(limit=5)
    # Преобразуем словари обратно в объекты User для совместимости с шаблонами
    best_members = []
    for member_dict in best_members_dicts:
        try:
            user_obj = User.objects.get(id=member_dict["id"])
            best_members.append(user_obj)
        except User.DoesNotExist:
            continue

    return {"user": user, "best_members": best_members}
