"""
Интерфейс для работы с тегами
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from django.db.models import QuerySet


class ITagRepository(ABC):
    """Интерфейс для получения данных о тегах"""

    @abstractmethod
    def get_all_tags(self) -> QuerySet | list[str]:
        """
        Получить все теги

        Returns:
            QuerySet или list: Список всех тегов
        """

    @abstractmethod
    def get_tag_info(self, tag_name: str) -> dict[str, Any]:
        """
        Получить информацию о теге

        Args:
            tag_name (str): Название тега

        Returns:
            dict: Информация о теге (название, количество вопросов и т.д.)
        """
