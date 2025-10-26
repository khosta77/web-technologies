"""
Интерфейс для работы с пользователями
"""
from abc import ABC, abstractmethod


class IUserRepository(ABC):
    """Интерфейс для получения данных о пользователях"""
    
    @abstractmethod
    def authenticate(self, username, password):
        """
        Аутентифицировать пользователя
        
        Args:
            username (str): Имя пользователя
            password (str): Пароль
            
        Returns:
            dict: Данные пользователя или None
        """
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id):
        """
        Получить пользователя по ID
        
        Args:
            user_id (int): ID пользователя
            
        Returns:
            dict: Данные пользователя
        """
        pass
    
    @abstractmethod
    def get_user_by_username(self, username):
        """
        Получить пользователя по username
        
        Args:
            username (str): Имя пользователя
            
        Returns:
            dict: Данные пользователя
        """
        pass
    
    @abstractmethod
    def get_user_questions(self, user_id):
        """
        Получить вопросы пользователя
        
        Args:
            user_id (int): ID пользователя
            
        Returns:
            list: Список вопросов пользователя
        """
        pass
    
    @abstractmethod
    def get_user_answers(self, user_id):
        """
        Получить ответы пользователя
        
        Args:
            user_id (int): ID пользователя
            
        Returns:
            list: Список ответов пользователя
        """
        pass

