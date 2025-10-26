"""
Mock репозиторий для работы с вопросами
"""

from app.interfaces import IQuestionRepository

from .mock_data_frames import HOT_QUESTIONS, NEW_QUESTIONS


class QuestionMockRepository(IQuestionRepository):
    """Реализация интерфейса IQuestionRepository с mock данными"""

    def get_all_questions(self):
        """Получить все вопросы (заглушка)"""
        # Возвращаем реалистичные данные из mock_data_frames
        return NEW_QUESTIONS.copy()

    def get_hot_questions(self):
        """Получить популярные вопросы (заглушка)"""
        # Возвращаем реалистичные данные из mock_data_frames (отсортированы по рейтингу)
        return HOT_QUESTIONS.copy()

    def get_questions_by_tag(self, tag_name):
        """Получить вопросы по тегу (заглушка)"""
        # Фильтруем вопросы, которые содержат указанный тег
        matching_questions = []
        for q in NEW_QUESTIONS:
            if tag_name.lower() in [t.lower() for t in q["tags"]]:
                q_copy = q.copy()
                # Оставляем только релевантный тег
                q_copy["tags"] = [tag_name]
                matching_questions.append(q_copy)

        # Если не нашли - генерируем некоторые вопросы по тегу
        if not matching_questions:
            for i, q in enumerate(NEW_QUESTIONS[:5], 1):
                matching_questions.append(
                    {
                        "id": q["id"],
                        "title": q["title"].replace("Django", tag_name).replace("React", tag_name),
                        "text": f"This question is related to {tag_name}...",
                        "author": q["author"],
                        "rating": q["rating"] - i,
                        "answers_count": q["answers_count"],
                        "tags": [tag_name],
                    }
                )

        return matching_questions

    def get_question_by_id(self, question_id):
        """Получить вопрос по ID (заглушка)"""
        # Ищем в NEW_QUESTIONS
        for q in NEW_QUESTIONS:
            if q["id"] == question_id:
                return q.copy()

        # Ищем в HOT_QUESTIONS
        for q in HOT_QUESTIONS:
            if q["id"] == question_id:
                return q.copy()

        # Если не найдено, возвращаем первую вопрос с обновленным ID
        q = NEW_QUESTIONS[0].copy()
        q["id"] = question_id
        return q
