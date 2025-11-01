"""Mock репозитории для тестирования"""

from .answer_mock_repository import AnswerMockRepository
from .question_mock_repository import QuestionMockRepository
from .tag_mock_repository import TagMockRepository
from .user_mock_repository import UserMockRepository


__all__ = [
    "AnswerMockRepository",
    "QuestionMockRepository",
    "TagMockRepository",
    "UserMockRepository",
]
