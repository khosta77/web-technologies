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
