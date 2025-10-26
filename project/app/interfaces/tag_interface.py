"""
Интерфейс для работы с тегами
"""
from abc import ABC, abstractmethod


class ITagRepository(ABC):
    """Интерфейс для получения данных о тегах"""
    
    @abstractmethod
    def get_all_tags(self):
        """
        Получить все теги
        
        Returns:
            list: Список всех тегов
        """
        pass
    
    @abstractmethod
    def get_tag_info(self, tag_name):
        """
        Получить информацию о теге
        
        Args:
            tag_name (str): Название тега
            
        Returns:
            dict: Информация о теге (название, количество вопросов и т.д.)
        """
        pass

