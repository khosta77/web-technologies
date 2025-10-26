"""
Mock репозиторий для работы с пользователями
"""

from app.interfaces import IUserRepository

from .mock_users import (
    MOCK_USERS,
    authenticate_user,
    get_user_answers,
    get_user_by_id as mock_get_user_by_id,
    get_user_by_username,
    get_user_questions,
)


class UserMockRepository(IUserRepository):
    """Реализация интерфейса IUserRepository с mock данными"""

    def authenticate(self, username, password):
        """Аутентифицировать пользователя"""
        return authenticate_user(username, password)

    def get_user_by_id(self, user_id):
        """Получить пользователя по ID"""
        return mock_get_user_by_id(user_id)

    def get_user_by_username(self, username):
        """Получить пользователя по username"""
        return get_user_by_username(username)

    def get_user_questions(self, user_id):
        """Получить вопросы пользователя"""
        return get_user_questions(user_id)

    def get_user_answers(self, user_id):
        """Получить ответы пользователя"""
        return get_user_answers(user_id)

    def get_all_users(self):
        """Получить всех пользователей (для тестирования)"""
        return MOCK_USERS.copy()

    def get_best_members(self, limit=5):
        """Получить лучших пользователей по рейтингу"""
        all_users = self.get_all_users()
        sorted_users = sorted(all_users, key=lambda x: x.get("rating", 0), reverse=True)
        return sorted_users[:limit]
