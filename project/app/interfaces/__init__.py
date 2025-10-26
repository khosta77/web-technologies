"""Интерфейсы для работы с данными"""
from .question_interface import IQuestionRepository
from .answer_interface import IAnswerRepository
from .tag_interface import ITagRepository
from .user_interface import IUserRepository

__all__ = [
    'IQuestionRepository',
    'IAnswerRepository',
    'ITagRepository',
    'IUserRepository',
]

