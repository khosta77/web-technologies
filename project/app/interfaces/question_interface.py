"""
Интерфейс для работы с вопросами
"""
from abc import ABC, abstractmethod


class IQuestionRepository(ABC):
    """Интерфейс для получения данных о вопросах"""
    
    @abstractmethod
    def get_all_questions(self):
        """
        Получить все вопросы
        
        Returns:
            list: Список всех вопросов
        """
        pass
    
    @abstractmethod
    def get_hot_questions(self):
        """
        Получить популярные вопросы (отсортированные по рейтингу)
        
        Returns:
            list: Список популярных вопросов
        """
        pass
    
    @abstractmethod
    def get_questions_by_tag(self, tag_name):
        """
        Получить вопросы по тегу
        
        Args:
            tag_name (str): Название тега
            
        Returns:
            list: Список вопросов по тегу
        """
        pass
    
    @abstractmethod
    def get_question_by_id(self, question_id):
        """
        Получить вопрос по ID
        
        Args:
            question_id (int): ID вопроса
            
        Returns:
            dict: Данные вопроса
        """
        pass

