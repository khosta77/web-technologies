"""
Репозиторий для работы с пользователями через Django ORM
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth.models import User

from app.models import Answer, Question


class UserRepository:
    """Репозиторий для работы с пользователями через Django ORM"""

    def authenticate(self, username: str, password: str) -> User | None:
        """Аутентифицировать пользователя"""
        return django_authenticate(username=username, password=password)

    def get_user_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID с оптимизацией запросов"""
        try:
            return User.objects.select_related("profile", "profile__avatar").get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_user_by_username(self, username: str) -> User | None:
        """Получить пользователя по username"""
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_user_questions(self, user_id: int) -> list[dict[str, Any]]:
        """Получить вопросы пользователя с оптимизацией запросов"""
        try:
            questions = (
                Question.objects.filter(author_id=user_id)
                .select_related("author__profile__avatar")
                .prefetch_related("tags")
            )
            return [self._question_to_dict(q) for q in questions]
        except User.DoesNotExist:
            return []

    def get_user_answers(self, user_id: int) -> list[dict[str, Any]]:
        """Получить ответы пользователя с оптимизацией запросов"""
        try:
            answers = Answer.objects.filter(author_id=user_id).select_related(
                "author__profile__avatar", "question"
            )
            return [self._answer_to_dict(a) for a in answers]
        except User.DoesNotExist:
            return []

    def get_best_members(self, limit: int = 5) -> list[dict[str, Any]]:
        """Получить лучших пользователей по рейтингу с оптимизацией запросов"""
        best_members = (
            User.objects.select_related("profile", "profile__avatar")
            .filter(profile__rating__gt=0)
            .order_by("-profile__rating")[:limit]
        )
        return [self._user_to_dict(user) for user in best_members]

    @staticmethod
    def _user_to_dict(user: User) -> dict[str, Any]:
        """Преобразовать модель User в словарь"""
        rating = 0
        if hasattr(user, "profile"):
            rating = user.profile.rating

        questions_count = getattr(user, "questions_count", None)
        if questions_count is None:
            questions_count = user.questions.count() if hasattr(user, "questions") else 0

        answers_count = getattr(user, "answers_count", None)
        if answers_count is None:
            answers_count = user.answers.count() if hasattr(user, "answers") else 0

        avatar_name = "img/avatar.jpg"
        if hasattr(user, "profile") and user.profile.avatar:
            avatar_name = user.profile.avatar.file.name

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rating": rating,
            "questions_count": questions_count,
            "answers_count": answers_count,
            "avatar": avatar_name,
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
            "tags": (
                [tag.name for tag in question._prefetched_objects_cache["tags"]]
                if hasattr(question, "_prefetched_objects_cache")
                and "tags" in question._prefetched_objects_cache
                else [tag.name for tag in question.tags.all()]
            ),
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
