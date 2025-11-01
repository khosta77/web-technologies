"""
Mock репозиторий для работы с ответами
"""

from app.interfaces import IAnswerRepository

from .mock_data_frames import SAMPLE_ANSWERS


class AnswerMockRepository(IAnswerRepository):
    """Реализация интерфейса IAnswerRepository с mock данными"""

    def get_answers_by_question_id(self, question_id):
        """Получить ответы на вопрос (заглушка)"""
        # Возвращаем реалистичные ответы из mock_data_frames
        return SAMPLE_ANSWERS.copy()
