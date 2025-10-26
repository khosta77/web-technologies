"""Интерфейсы для работы с данными"""

from .answer_interface import IAnswerRepository
from .question_interface import IQuestionRepository
from .tag_interface import ITagRepository
from .user_interface import IUserRepository


__all__ = [
    "IAnswerRepository",
    "IQuestionRepository",
    "ITagRepository",
    "IUserRepository",
]
