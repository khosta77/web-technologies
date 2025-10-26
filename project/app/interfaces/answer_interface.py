"""
Интерфейс для работы с ответами
"""
from abc import ABC, abstractmethod


class IAnswerRepository(ABC):
    """Интерфейс для получения данных об ответах"""
    
    @abstractmethod
    def get_answers_by_question_id(self, question_id):
        """
        Получить все ответы на вопрос
        
        Args:
            question_id (int): ID вопроса
            
        Returns:
            list: Список ответов на вопрос
        """
        pass

