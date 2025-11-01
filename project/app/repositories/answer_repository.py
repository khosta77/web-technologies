"""
Репозиторий для работы с ответами через Django ORM
"""

from __future__ import annotations

from django.db.models import QuerySet

from app.interfaces import IAnswerRepository
from app.models import Answer, Question


class AnswerRepository(IAnswerRepository):
    """Реализация интерфейса IAnswerRepository с использованием Django ORM"""

    def get_answers_by_question_id(self, question_id: int) -> QuerySet:
        """Получить все ответы на вопрос"""
        try:
            question = Question.objects.get(id=question_id)
            return question.answers.all()
        except Question.DoesNotExist:
            return Answer.objects.none()
