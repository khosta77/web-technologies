"""
Тесты для UserMockRepository
"""

from app.mockRepositories.mock_users import MOCK_USERS
from app.mockRepositories.user_mock_repository import UserMockRepository


class TestUserMockRepository:
    """Тесты для UserMockRepository"""

    def test_setup_method(self):
        """Инициализация перед каждым тестом"""
        repository = UserMockRepository()
        assert repository is not None

    def test_authenticate_success(self):
        """Тест успешной аутентификации"""
        repository = UserMockRepository()
        user = repository.authenticate("python_dev", "12345")

        assert user is not None
        assert user["username"] == "python_dev"
        assert user["email"] == "dev@example.com"

    def test_authenticate_failure_wrong_password(self):
        """Тест неудачной аутентификации с неверным паролем"""
        repository = UserMockRepository()
        user = repository.authenticate("python_dev", "wrong_password")

        assert user is None

    def test_authenticate_failure_wrong_username(self):
        """Тест неудачной аутентификации с неверным username"""
        repository = UserMockRepository()
        user = repository.authenticate("nonexistent_user", "12345")

        assert user is None

    def test_get_user_by_id_success(self):
        """Тест получения пользователя по ID"""
        repository = UserMockRepository()
        user = repository.get_user_by_id(1)

        assert user is not None
        assert user["id"] == 1
        assert user["username"] == "python_dev"

    def test_get_user_by_id_not_found(self):
        """Тест получения пользователя по несуществующему ID"""
        repository = UserMockRepository()
        user = repository.get_user_by_id(999)

        assert user is None

    def test_get_user_by_username_success(self):
        """Тест получения пользователя по username"""
        repository = UserMockRepository()
        user = repository.get_user_by_username("django_master")

        assert user is not None
        assert user["username"] == "django_master"
        assert user["email"] == "master@example.com"

    def test_get_user_by_username_not_found(self):
        """Тест получения пользователя по несуществующему username"""
        repository = UserMockRepository()
        user = repository.get_user_by_username("nonexistent")

        assert user is None

    def test_get_all_users(self):
        """Тест получения всех пользователей"""
        repository = UserMockRepository()
        users = repository.get_all_users()

        assert len(users) == len(MOCK_USERS)
        assert isinstance(users, list)
        # Проверяем, что вернулась копия
        assert users is not MOCK_USERS

    def test_get_best_members(self):
        """Тест получения лучших пользователей"""
        repository = UserMockRepository()
        best = repository.get_best_members(limit=5)

        assert len(best) == 5

        # Проверяем, что пользователи отсортированы по рейтингу
        ratings = [user["rating"] for user in best]
        assert ratings == sorted(ratings, reverse=True)

        # Проверяем, что все имеют ненулевой рейтинг
        assert all(user["rating"] > 0 for user in best)

    def test_get_best_members_custom_limit(self):
        """Тест получения лучших пользователей с кастомным лимитом"""
        repository = UserMockRepository()
        best = repository.get_best_members(limit=3)

        assert len(best) == 3

    def test_get_user_questions(self):
        """Тест получения вопросов пользователя"""
        repository = UserMockRepository()
        questions = repository.get_user_questions(1)

        assert isinstance(questions, list)
        assert len(questions) > 0
        assert all(q["author_id"] == 1 for q in questions)

    def test_get_user_answers(self):
        """Тест получения ответов пользователя"""
        repository = UserMockRepository()
        answers = repository.get_user_answers(1)

        assert isinstance(answers, list)
        assert len(answers) > 0
        assert all(a["author_id"] == 1 for a in answers)
