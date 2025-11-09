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

    def test_index_page_renders_correctly(self):
        """Тест: главная страница отображается без ошибок"""
        response = self.client.get("/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        # Проверяем только критические ошибки Django
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content
        # Проверяем наличие ключевых элементов
        assert "AskPupkin" in content or "askpupkin" in content.lower()

    def test_index_page_has_no_template_errors(self):
        """Тест: страница не содержит ошибок шаблона"""
        response = self.client.get("/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        # Проверяем, что нет типичных ошибок Django
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "KeyError" not in content
        assert "TypeError" not in content

    def test_hot_page_renders_correctly(self):
        """Тест: страница горячих вопросов отображается без ошибок"""
        response = self.client.get("/hot/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        # Проверяем только критические ошибки Django
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content

    def test_tags_page_renders_correctly(self):
        """Тест: страница тегов отображается без ошибок"""
        response = self.client.get("/tags/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        # Проверяем только критические ошибки Django
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content
        # Проверяем наличие тега
        assert "python" in content.lower()

    def test_question_page_renders_correctly(self):
        """Тест: страница вопроса отображается без ошибок"""
        response = self.client.get(f"/question/{self.question.id}/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        # Проверяем только критические ошибки Django
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content
        # Проверяем наличие вопроса
        assert "Test Question" in content

    def test_tag_page_renders_correctly(self):
        """Тест: страница тега отображается без ошибок"""
        response = self.client.get("/tag/python/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        # Проверяем только критические ошибки Django
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content

    def test_login_page_renders_correctly(self):
        """Тест: страница входа отображается без ошибок"""
        response = self.client.get("/login/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        # Проверяем только критические ошибки Django
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content
        assert "Log In" in content or "login" in content.lower()

    def test_signup_page_renders_correctly(self):
        """Тест: страница регистрации отображается без ошибок"""
        response = self.client.get("/register/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        # Проверяем только критические ошибки Django, игнорируя нормальные слова в комментариях
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content
        assert "Registration" in content or "register" in content.lower()

    def test_profile_page_renders_correctly(self):
        """Тест: страница профиля отображается без ошибок"""
        response = self.client.get(f"/profile/{self.user.id}/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        # Проверяем только критические ошибки Django
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content
        # Проверяем наличие имени пользователя
        assert "testuser" in content.lower()

    def test_404_page_renders_correctly(self):
        """Тест: страница 404 отображается без ошибок"""
        response = self.client.get("/nonexistent-page/")

        assert response.status_code == 404
        content = response.content.decode("utf-8")
        # Проверяем только критические ошибки Django (404 - это нормально)
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content
        # Проверяем, что это наша кастомная страница 404
        assert "404" in content or "not found" in content.lower()

    def test_all_pages_have_no_database_errors(self):
        """Тест: все основные страницы не содержат ошибок БД"""
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
                # Проверяем отсутствие ошибок БД
                assert "DatabaseError" not in content
                assert "OperationalError" not in content
                assert "ProgrammingError" not in content
                assert "IntegrityError" not in content

    def test_pages_have_no_template_syntax_errors(self):
        """Тест: все страницы не содержат синтаксических ошибок шаблонов"""
        pages = [
            "/",
            "/hot/",
            "/tags/",
            f"/question/{self.question.id}/",
            "/tag/python/",
            "/login/",
            "/register/",
        ]

        for page in pages:
            response = self.client.get(page)
            assert response.status_code == 200, f"Page {page} failed"
            content = response.content.decode("utf-8")
            # Проверяем отсутствие ошибок шаблонов
            assert "TemplateSyntaxError" not in content
            assert "TemplateDoesNotExist" not in content
            assert "{%" not in content or "%}" in content  # Проверяем корректность тегов шаблона
