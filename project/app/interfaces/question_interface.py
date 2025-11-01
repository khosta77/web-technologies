"""
Интерфейс для работы с вопросами
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IQuestionRepository(ABC):
    """Интерфейс для получения данных о вопросах"""

    @abstractmethod
    def get_all_questions(self) -> list[dict[str, Any]]:
        """
        Получить все вопросы

        Returns:
            list: Список всех вопросов
        """

    @abstractmethod
    def get_hot_questions(self) -> list[dict[str, Any]]:
        """
        Получить популярные вопросы (отсортированные по рейтингу)

        Returns:
            list: Список популярных вопросов
        """

    @abstractmethod
    def get_questions_by_tag(self, tag_name: str) -> list[dict[str, Any]]:
        """
        Получить вопросы по тегу

        Args:
            tag_name (str): Название тега

        Returns:
            list: Список вопросов по тегу
        """

    @abstractmethod
    def get_question_by_id(self, question_id: int) -> dict[str, Any]:
        """
        Получить вопрос по ID

        Args:
            question_id (int): ID вопроса

        Returns:
            dict: Данные вопроса
        """
