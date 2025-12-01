"""
Репозиторий для работы с вопросами через Django ORM
"""

from __future__ import annotations

from django.db.models import Count, QuerySet

from app.interfaces import IQuestionRepository
from app.models import Question


class QuestionRepository(IQuestionRepository):
    """Реализация интерфейса IQuestionRepository с использованием Django ORM"""

    def get_all_questions(self) -> QuerySet:
        """Получить все вопросы (новые)"""
        return (
            Question.objects.new()
            .select_related("author", "author__profile", "author__profile__avatar")
            .prefetch_related("tags")
            .annotate(answers_count=Count("answers"))
        )

    def get_hot_questions(self) -> QuerySet:
        """Получить популярные вопросы"""
        return (
            Question.objects.hot()
            .select_related("author", "author__profile", "author__profile__avatar")
            .prefetch_related("tags")
            .annotate(answers_count=Count("answers"))
        )

    def get_questions_by_tag(self, tag_name: str) -> QuerySet:
        """Получить вопросы по тегу"""
        return (
            Question.objects.by_tag(tag_name)
            .select_related("author", "author__profile", "author__profile__avatar")
            .prefetch_related("tags")
            .annotate(answers_count=Count("answers"))
        )

    def get_question_by_id(self, question_id: int) -> Question | None:
        """Получить вопрос по ID"""
        try:
            question = (
                Question.objects.select_related(
                    "author", "author__profile", "author__profile__avatar"
                )
                .prefetch_related("tags")
                .get(id=question_id)
            )
            return question  # type: ignore[no-any-return]
        except Question.DoesNotExist:
            return None
