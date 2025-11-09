"""
Репозиторий для работы с ответами через Django ORM
"""

from __future__ import annotations

from django.db.models import QuerySet

from app.interfaces import IAnswerRepository
from app.models import Answer


class AnswerRepository(IAnswerRepository):
    """Реализация интерфейса IAnswerRepository с использованием Django ORM"""

    def get_answers_by_question_id(self, question_id: int) -> QuerySet:
        """Получить все ответы на вопрос с оптимизацией запросов"""
        return (
            Answer.objects.filter(question_id=question_id)
            .select_related("author", "author__profile", "question")
            .order_by("-rating", "-created_at")
        )
