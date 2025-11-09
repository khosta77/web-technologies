"""Репозитории для работы с данными через Django ORM"""

from .answer_repository import AnswerRepository
from .question_repository import QuestionRepository
from .tag_repository import TagRepository
from .user_repository import UserRepository


__all__ = [
    "AnswerRepository",
    "QuestionRepository",
    "TagRepository",
    "UserRepository",
]
