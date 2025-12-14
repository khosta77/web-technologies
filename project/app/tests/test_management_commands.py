"""
Тесты для management commands
"""

from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from app.models import Profile


class GetUserInfoCommandTestCase(TestCase):
    """Тесты для команды get_user_info"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="12345"
        )
        Profile.objects.create(user=self.user, rating=100)

    def test_get_user_info_success(self):
        """Тест: команда успешно выводит информацию о пользователе"""
        out = StringIO()
        call_command("get_user_info", str(self.user.id), stdout=out)
        output = out.getvalue()

        assert "ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ" in output
        assert f"ID: {self.user.id}" in output
        assert f"Username: {self.user.username}" in output
        assert f"Email: {self.user.email}" in output
        assert f"URL профиля: http://127.0.0.1:8000/profile/{self.user.id}/" in output

    def test_get_user_info_with_profile(self):
        """Тест: команда выводит информацию о профиле"""
        out = StringIO()
        call_command("get_user_info", str(self.user.id), stdout=out)
        output = out.getvalue()

        assert "ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ" in output
        assert "Рейтинг: 100" in output
        assert "Вопросов: 0" in output
        assert "Ответов: 0" in output

    def test_get_user_info_with_test_password(self):
        """Тест: команда определяет стандартный тестовый пароль"""
        out = StringIO()
        call_command("get_user_info", str(self.user.id), stdout=out)
        output = out.getvalue()

        assert "ДАННЫЕ ДЛЯ ВХОДА" in output
        assert f"Логин: {self.user.username}" in output
        assert "Пароль: 12345" in output
        assert "✓ Пароль подтвержден" in output

    def test_get_user_info_user_not_found(self):
        """Тест: команда обрабатывает несуществующего пользователя"""
        out = StringIO()
        err = StringIO()
        call_command("get_user_info", "99999", stdout=out, stderr=err)
        output = out.getvalue()

        assert "не найден в базе данных" in output
        assert "Используйте команду для получения списка пользователей" in output

    def test_get_user_info_with_questions_and_answers(self):
        """Тест: команда выводит количество вопросов и ответов"""
        from app.models import Answer, Question

        question = Question.objects.create(
            title="Test Question", text="Test text", author=self.user
        )
        Answer.objects.create(text="Test answer", author=self.user, question=question)

        out = StringIO()
        call_command("get_user_info", str(self.user.id), stdout=out)
        output = out.getvalue()

        assert "Вопросов: 1" in output
        assert "Ответов: 1" in output


class ListUsersCommandTestCase(TestCase):
    """Тесты для команды list_users"""

    def test_list_users_empty(self):
        """Тест: команда обрабатывает пустую базу данных"""
        out = StringIO()
        call_command("list_users", stdout=out)
        output = out.getvalue()

        assert "В базе данных нет пользователей" in output

    def test_list_users_single_user(self):
        """Тест: команда выводит одного пользователя"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        out = StringIO()
        call_command("list_users", stdout=out)
        output = out.getvalue()

        assert "СПИСОК ПОЛЬЗОВАТЕЛЕЙ" in output
        assert f"{user.id}: {user.username}" in output
        assert "Всего пользователей: 1" in output

    def test_list_users_multiple_users(self):
        """Тест: команда выводит нескольких пользователей"""
        user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="testpass123"
        )

        out = StringIO()
        call_command("list_users", stdout=out)
        output = out.getvalue()

        assert "СПИСОК ПОЛЬЗОВАТЕЛЕЙ" in output
        assert f"{user1.id}: {user1.username}" in output
        assert f"{user2.id}: {user2.username}" in output
        assert f"{user3.id}: {user3.username}" in output
        assert "Всего пользователей: 3" in output

    def test_list_users_ordered_by_id(self):
        """Тест: команда выводит пользователей отсортированных по ID"""
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="testpass123"
        )

        out = StringIO()
        call_command("list_users", stdout=out)
        output = out.getvalue()

        # Проверяем, что все пользователи присутствуют в выводе
        assert f"{user1.id}: {user1.username}" in output
        assert f"{user2.id}: {user2.username}" in output
        assert f"{user3.id}: {user3.username}" in output

        # Проверяем, что пользователи отсортированы по ID
        lines = output.split("\n")
        user_lines = [
            line
            for line in lines
            if ":" in line
            and line.strip()
            and "СПИСОК" not in line
            and "Всего" not in line
            and "=" not in line
        ]

        # Должны быть в порядке возрастания ID
        ids = []
        for line in user_lines:
            if ":" in line:
                user_id = int(line.split(":")[0].strip())
                ids.append(user_id)

        assert ids == sorted(ids), "Пользователи должны быть отсортированы по ID"
