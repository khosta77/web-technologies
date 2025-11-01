"""
Репозиторий для работы с пользователями через Django ORM
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth.models import User
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from app.interfaces import IUserRepository
from app.models import Answer, Question  # noqa: TC001


class UserRepository(IUserRepository):
    """Реализация интерфейса IUserRepository с использованием Django ORM"""

    def authenticate(self, username: str, password: str) -> User | None:
        """Аутентифицировать пользователя"""
        return django_authenticate(username=username, password=password)

    def get_user_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_user_by_username(self, username: str) -> User | None:
        """Получить пользователя по username"""
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_user_questions(self, user_id: int) -> list[dict[str, Any]]:
        """Получить вопросы пользователя"""
        try:
            user = User.objects.get(id=user_id)
            questions = user.questions.all()
            return [self._question_to_dict(q) for q in questions]
        except User.DoesNotExist:
            return []

    def get_user_answers(self, user_id: int) -> list[dict[str, Any]]:
        """Получить ответы пользователя"""
        try:
            user = User.objects.get(id=user_id)
            answers = user.answers.all()
            return [self._answer_to_dict(a) for a in answers]
        except User.DoesNotExist:
            return []

    def get_best_members(self, limit: int = 5) -> list[dict[str, Any]]:
        """Получить лучших пользователей по рейтингу"""
        best_members = (
            User.objects.annotate(
                question_rating=Coalesce(Sum("questions__likes__value"), Value(0)),
                answer_rating=Coalesce(Sum("answers__likes__value"), Value(0)),
            )
            .annotate(
                rating=Coalesce(Sum("questions__likes__value"), Value(0))
                + Coalesce(Sum("answers__likes__value"), Value(0))
            )
            .order_by("-rating")
            .filter(rating__gt=0)[:limit]
        )
        return [self._user_to_dict(user) for user in best_members]

    @staticmethod
    def _user_to_dict(user: User) -> dict[str, Any]:
        """Преобразовать модель User в словарь"""
        rating = 0
        if hasattr(user, "profile"):
            rating = user.profile.get_rating()

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rating": rating,
            "questions_count": user.questions.count(),
            "answers_count": user.answers.count(),
            "avatar": user.profile.avatar.name if hasattr(user, "profile") else "img/avatar.jpg",
        }

    @staticmethod
    def _question_to_dict(question: Question) -> dict[str, Any]:
        """Преобразовать модель Question в словарь"""
        return {
            "id": question.id,
            "title": question.title,
            "text": question.text,
            "author": question.author.username,
            "author_id": question.author.id,
            "rating": question.rating,
            "answers_count": question.get_answers_count(),
            "created_at": question.created_at,
            "tags": [tag.name for tag in question.tags.all()],
        }

    @staticmethod
    def _answer_to_dict(answer: Answer) -> dict[str, Any]:
        """Преобразовать модель Answer в словарь"""
        return {
            "id": answer.id,
            "text": answer.text,
            "author": answer.author.username,
            "author_id": answer.author.id,
            "question_id": answer.question.id,
            "rating": answer.rating,
            "is_correct": answer.is_correct,
            "created_at": answer.created_at,
        }
