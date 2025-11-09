"""
Интерфейс для работы с ответами
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from django.db.models import QuerySet


class IAnswerRepository(ABC):
    """Интерфейс для получения данных об ответах"""

    @abstractmethod
    def get_answers_by_question_id(self, question_id: int) -> QuerySet | list[dict[str, Any]]:
        """
        Получить все ответы на вопрос

        Args:
            question_id (int): ID вопроса

        Returns:
            QuerySet или list: Список ответов на вопрос
        """
