"""
Интерфейс для работы с пользователями
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IUserRepository(ABC):
    """Интерфейс для получения данных о пользователях"""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Any:
        """
        Аутентифицировать пользователя

        Args:
            username (str): Имя пользователя
            password (str): Пароль

        Returns:
            User или dict: Объект пользователя или словарь с данными, или None
        """

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Any:
        """
        Получить пользователя по ID

        Args:
            user_id (int): ID пользователя

        Returns:
            User или dict: Объект пользователя или словарь с данными, или None
        """

    @abstractmethod
    def get_user_by_username(self, username: str) -> Any:
        """
        Получить пользователя по username

        Args:
            username (str): Имя пользователя

        Returns:
            User или dict: Объект пользователя или словарь с данными, или None
        """

    @abstractmethod
    def get_user_questions(self, user_id: int) -> list[dict[str, Any]]:
        """
        Получить вопросы пользователя

        Args:
            user_id (int): ID пользователя

        Returns:
            list: Список вопросов пользователя
        """

    @abstractmethod
    def get_user_answers(self, user_id: int) -> list[dict[str, Any]]:
        """
        Получить ответы пользователя

        Args:
            user_id (int): ID пользователя

        Returns:
            list: Список ответов пользователя
        """

    @abstractmethod
    def get_best_members(self, limit: int = 5) -> list[dict[str, Any]]:
        """
        Получить лучших пользователей по рейтингу

        Args:
            limit (int): Количество пользователей

        Returns:
            list: Список пользователей
        """
