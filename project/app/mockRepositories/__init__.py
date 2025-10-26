"""Mock репозитории для тестирования"""
from .question_mock_repository import QuestionMockRepository
from .answer_mock_repository import AnswerMockRepository
from .tag_mock_repository import TagMockRepository

__all__ = [
    'QuestionMockRepository',
    'AnswerMockRepository',
    'TagMockRepository',
]

