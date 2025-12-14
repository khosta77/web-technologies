"""
Интеграционные тесты для проверки корректности отображения страниц
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.test import Client, TestCase

from app.models import Answer, Question, Tag


class IntegrationTestCase(TestCase):
    """Тесты для проверки корректности отображения страниц"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.tag = Tag.objects.create(name="python")
        self.question = Question.objects.create(
            title="Test Question",
            text="Test question text",
            author=self.user,
        )
        self.question.tags.add(self.tag)
        self.answer = Answer.objects.create(
            text="Test answer text",
            author=self.user,
            question=self.question,
        )

    def _check_content_for_errors(self, content: str) -> None:
        """Вспомогательный метод для проверки отсутствия ошибок в контенте"""
        # Проверяем критические ошибки Django
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content
        assert "KeyError" not in content
        assert "TypeError" not in content
        assert "DatabaseError" not in content
        assert "OperationalError" not in content
        assert "ProgrammingError" not in content
        assert "IntegrityError" not in content

    def test_all_pages_have_no_errors(self):
        """Тест: все основные страницы не содержат ошибок"""
        pages = [
            "/",
            "/hot/",
            "/tags/",
            f"/question/{self.question.id}/",
            "/tag/python/",
            "/login/",
            "/register/",
            f"/profile/{self.user.id}/",
        ]

        for page in pages:
            response = self.client.get(page)
            assert response.status_code in [200, 302], (
                f"Page {page} returned {response.status_code}"
            )
            if response.status_code == 200:
                content = response.content.decode("utf-8")
                self._check_content_for_errors(content)
                # Проверяем отсутствие ошибок шаблонов
                assert "TemplateDoesNotExist" not in content

    def test_404_page_renders_correctly(self):
        """Тест: страница 404 отображается без ошибок"""
        response = self.client.get("/nonexistent-page/")

        assert response.status_code == 404
        content = response.content.decode("utf-8")
        # Проверяем только критические ошибки Django (404 - это нормально)
        self._check_content_for_errors(content)
        # Проверяем, что это наша кастомная страница 404
        assert "404" in content or "not found" in content.lower()

    def test_question_page_with_answer_renders_correctly(self):
        """Тест: страница вопроса с ответом отображается без ошибок"""
        response = self.client.get(f"/question/{self.question.id}/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        self._check_content_for_errors(content)
        # Проверяем наличие вопроса и ответа
        assert "Test Question" in content
        assert "Test answer text" in content
