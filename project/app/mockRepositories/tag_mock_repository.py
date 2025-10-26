"""
Mock репозиторий для работы с тегами
"""

from app.interfaces import ITagRepository

from .mock_data_frames import ALL_TAGS


class TagMockRepository(ITagRepository):
    """Реализация интерфейса ITagRepository с mock данными"""

    def get_all_tags(self):
        """Получить все теги (заглушка)"""
        return ALL_TAGS.copy()

    def get_tag_info(self, tag_name):
        """Получить информацию о теге"""
        # Подсчитываем количество вопросов с этим тегом
        from app.mockRepositories.question_mock_repository import QuestionMockRepository

        question_repo = QuestionMockRepository()
        questions_with_tag = question_repo.get_questions_by_tag(tag_name)

        return {
            "name": tag_name,
            "questions_count": len(questions_with_tag),
            "related_tags": ["python", "django", "javascript", "react"],
        }
