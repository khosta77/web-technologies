"""
Тесты для views
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.test import Client, TestCase

from app.models import Answer, Question, Tag


class ViewsTestCase(TestCase):
    """Тесты для views"""

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

    def test_index_status_code(self):
        """Тест статуса главной страницы"""
        response = self.client.get("/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content

    def test_hot_status_code(self):
        """Тест статуса страницы горячих вопросов"""
        response = self.client.get("/hot/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content

    def test_tags_status_code(self):
        """Тест статуса страницы тегов"""
        response = self.client.get("/tags/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content

    def test_question_status_code(self):
        """Тест статуса страницы вопроса"""
        response = self.client.get(f"/question/{self.question.id}/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content
        assert "Test Question" in content

    def test_question_not_found(self):
        """Тест несуществующего вопроса"""
        response = self.client.get("/question/99999/")

        # Должен быть 404
        assert response.status_code == 404

    def test_tag_page_status_code(self):
        """Тест статуса страницы с вопросами по тегу"""
        response = self.client.get("/tag/python/")

        assert response.status_code == 200

    def test_login_page_status_code(self):
        """Тест статуса страницы входа"""
        response = self.client.get("/login/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content

    def test_signup_page_status_code(self):
        """Тест статуса страницы регистрации"""
        response = self.client.get("/register/")

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "TemplateSyntaxError" not in content
        assert "DoesNotExist" not in content
        assert "AttributeError" not in content
        assert "Exception" not in content

    def test_login_success(self):
        """Тест успешного входа"""
        response = self.client.post("/login/", {"username": "testuser", "password": "testpass123"})

        # После успешного входа должен быть редирект
        assert response.status_code == 302

    def test_login_failure(self):
        """Тест неудачного входа"""
        response = self.client.post(
            "/login/", {"username": "testuser", "password": "wrong_password"}
        )

        # При неудачном входе должна вернуться форма
        assert response.status_code == 200

    def test_logout_redirect(self):
        """Тест выхода из системы"""
        # Сначала логинимся
        self.client.post("/login/", {"username": "testuser", "password": "testpass123"})

        # Затем выходим
        response = self.client.get("/logout/")

        # Должен быть редирект
        assert response.status_code == 302

    def test_ask_page_requires_login(self):
        """Тест что страница ask требует логина"""
        response = self.client.get("/ask/")

        # Должен быть редирект на логин
        assert response.status_code == 302

    def test_settings_page_requires_login(self):
        """Тест что страница settings требует логина"""
        response = self.client.get("/settings/")

        # Должен быть редирект на логин
        assert response.status_code == 302

    def test_settings_page_with_login(self):
        """Тест страницы settings с логином"""
        # Логинимся
        self.client.post("/login/", {"username": "testuser", "password": "testpass123"})

        response = self.client.get("/settings/")

        # Теперь должен быть доступ
        assert response.status_code == 200

    def test_profile_page(self):
        """Тест страницы профиля"""
        response = self.client.get(f"/profile/{self.user.id}/")

        assert response.status_code == 200

    def test_profile_not_found(self):
        """Тест несуществующего профиля"""
        response = self.client.get("/profile/99999/")

        # Должен быть 404
        assert response.status_code == 404

    def test_question_page_with_answers(self):
        """Тест страницы вопроса с ответами"""
        Answer.objects.create(text="Test answer", author=self.user, question=self.question)

        response = self.client.get(f"/question/{self.question.id}/")

        assert response.status_code == 200
        assert "Test answer" in response.content.decode()

    def test_hot_questions_sorted_by_rating(self):
        """Тест сортировки горячих вопросов"""
        Question.objects.create(
            title="Hot Question",
            text="Hot text",
            author=self.user,
            rating=10,
        )

        response = self.client.get("/hot/")
        assert response.status_code == 200

        # Проверяем, что вопрос с большим рейтингом первым
        content = response.content.decode()
        hot_index = content.find("Hot Question")
        test_index = content.find("Test Question")
        if hot_index != -1 and test_index != -1:
            assert hot_index < test_index

    def test_tag_filter_questions(self):
        """Тест фильтрации вопросов по тегу"""
        tag2 = Tag.objects.create(name="django")
        question2 = Question.objects.create(
            title="Django Question",
            text="Django text",
            author=self.user,
        )
        question2.tags.add(tag2)

        response = self.client.get("/tag/python/")
        assert response.status_code == 200

        content = response.content.decode()
        assert "Test Question" in content
        assert "Django Question" not in content

    def test_like_question_ajax_success(self):
        """Тест: AJAX лайк вопроса успешен"""
        self.client.post("/login/", {"username": "testuser", "password": "testpass123"})

        response = self.client.post(
            "/api/like/question/", {"question_id": self.question.id, "value": 1}
        )

        assert response.status_code == 200
        data = response.json()
        assert "rating" in data
        assert "removed" in data

    def test_like_question_ajax_requires_login(self):
        """Тест: AJAX лайк вопроса требует логина"""
        response = self.client.post(
            "/api/like/question/", {"question_id": self.question.id, "value": 1}
        )

        # Должен быть редирект на логин
        assert response.status_code == 302

    def test_like_question_ajax_invalid_data(self):
        """Тест: AJAX лайк вопроса с невалидными данными"""
        self.client.post("/login/", {"username": "testuser", "password": "testpass123"})

        response = self.client.post(
            "/api/like/question/", {"question_id": self.question.id, "value": 2}
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_like_answer_ajax_success(self):
        """Тест: AJAX лайк ответа успешен"""
        answer = Answer.objects.create(text="Test answer", author=self.user, question=self.question)
        self.client.post("/login/", {"username": "testuser", "password": "testpass123"})

        response = self.client.post("/api/like/answer/", {"answer_id": answer.id, "value": 1})

        assert response.status_code == 200
        data = response.json()
        assert "rating" in data
        assert "removed" in data

    def test_like_answer_ajax_requires_login(self):
        """Тест: AJAX лайк ответа требует логина"""
        answer = Answer.objects.create(text="Test answer", author=self.user, question=self.question)

        response = self.client.post("/api/like/answer/", {"answer_id": answer.id, "value": 1})

        # Должен быть редирект на логин
        assert response.status_code == 302

    def test_like_answer_ajax_requires_post(self):
        """Тест: AJAX лайк ответа требует POST"""
        answer = Answer.objects.create(text="Test answer", author=self.user, question=self.question)
        self.client.post("/login/", {"username": "testuser", "password": "testpass123"})

        response = self.client.get("/api/like/answer/", {"answer_id": answer.id, "value": 1})

        # Должен вернуть 405 Method Not Allowed
        assert response.status_code == 405

    def test_mark_correct_answer_ajax_success(self):
        """Тест: AJAX отметка правильного ответа успешна"""
        answer = Answer.objects.create(text="Test answer", author=self.user, question=self.question)
        self.client.post("/login/", {"username": "testuser", "password": "testpass123"})

        response = self.client.post(
            "/api/mark-correct/",
            {
                "question_id": self.question.id,
                "answer_id": answer.id,
                "is_correct": "true",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] is True
        assert data["is_correct"] is True

    def test_mark_correct_answer_ajax_requires_login(self):
        """Тест: AJAX отметка правильного ответа требует логина"""
        answer = Answer.objects.create(text="Test answer", author=self.user, question=self.question)

        response = self.client.post(
            "/api/mark-correct/",
            {
                "question_id": self.question.id,
                "answer_id": answer.id,
                "is_correct": "true",
            },
        )

        # Должен быть редирект на логин
        assert response.status_code == 302

    def test_mark_correct_answer_ajax_wrong_author(self):
        """Тест: AJAX отметка правильного ответа неавтором вопроса"""
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        answer = Answer.objects.create(
            text="Test answer", author=other_user, question=self.question
        )
        self.client.post("/login/", {"username": "otheruser", "password": "testpass123"})

        response = self.client.post(
            "/api/mark-correct/",
            {
                "question_id": self.question.id,
                "answer_id": answer.id,
                "is_correct": "true",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
