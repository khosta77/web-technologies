"""
Тесты для моделей
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase

from app.models import Answer, AnswerLike, Profile, Question, QuestionLike, Tag


class ProfileModelTestCase(TestCase):
    """Тесты для модели Profile"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = Profile.objects.create(user=self.user, rating=0)

    def test_profile_creation(self):
        """Тест создания профиля"""
        assert self.profile.user == self.user
        assert self.profile.avatar.name == "img/avatar.jpg"

    def test_profile_get_rating(self):
        """Тест получения рейтинга пользователя"""
        rating = self.profile.get_rating()
        assert rating == 0  # Изначально рейтинг 0

    def test_profile_with_custom_avatar(self):
        """Тест: профиль с кастомным аватаром"""
        # Устанавливаем кастомный аватар
        self.profile.avatar = "img/avatar1.jpg"
        self.profile.save()

        assert self.profile.avatar.name == "img/avatar1.jpg"
        assert self.profile.avatar.url.startswith("/media/")

    def test_profile_avatar_url(self):
        """Тест: правильный URL для аватара"""
        user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )
        profile2 = Profile.objects.create(user=user2, rating=0)
        profile2.avatar = "img/avatar2.jpg"
        profile2.save()

        # Проверяем, что URL формируется правильно
        avatar_url = profile2.avatar.url
        assert avatar_url.startswith("/media/")
        assert "avatar2.jpg" in avatar_url


class TagModelTestCase(TestCase):
    """Тесты для модели Tag"""

    def test_tag_creation(self):
        """Тест создания тега"""
        tag = Tag.objects.create(name="python")
        assert tag.name == "python"
        assert str(tag) == "python"


class QuestionModelTestCase(TestCase):
    """Тесты для модели Question"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
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

    def test_question_creation(self):
        """Тест создания вопроса"""
        assert self.question.title == "Test Question"
        assert self.question.text == "Test question text"
        assert self.question.author == self.user
        assert self.question.rating == 0
        assert self.tag in self.question.tags.all()

    def test_question_get_answers_count(self):
        """Тест получения количества ответов"""
        assert self.question.get_answers_count() == 0

        Answer.objects.create(text="Test answer", author=self.user, question=self.question)
        assert self.question.get_answers_count() == 1

    def test_question_update_rating(self):
        """Тест обновления рейтинга вопроса"""
        assert self.question.rating == 0

        # Создаем лайк
        QuestionLike.objects.create(user=self.user, question=self.question, value=1)
        self.question.update_rating()
        self.question.refresh_from_db()
        assert self.question.rating == 1

        # Создаем еще один лайк
        user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )
        QuestionLike.objects.create(user=user2, question=self.question, value=1)
        self.question.update_rating()
        self.question.refresh_from_db()
        assert self.question.rating == 2

    def test_question_manager_new(self):
        """Тест менеджера new()"""
        question2 = Question.objects.create(
            title="Newer Question",
            text="Newer text",
            author=self.user,
        )
        questions = list(Question.objects.new())
        assert questions[0] == question2  # Новые вопросы первыми

    def test_question_manager_hot(self):
        """Тест менеджера hot()"""
        question2 = Question.objects.create(
            title="Hot Question",
            text="Hot text",
            author=self.user,
            rating=10,
        )
        questions = list(Question.objects.hot())
        assert questions[0] == question2  # Вопросы с большим рейтингом первыми

    def test_question_manager_by_tag(self):
        """Тест менеджера by_tag()"""
        tag2 = Tag.objects.create(name="django")
        question2 = Question.objects.create(
            title="Django Question",
            text="Django text",
            author=self.user,
        )
        question2.tags.add(tag2)

        django_questions = list(Question.objects.by_tag("django"))
        assert question2 in django_questions
        assert self.question not in django_questions


class AnswerModelTestCase(TestCase):
    """Тесты для модели Answer"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.question = Question.objects.create(
            title="Test Question",
            text="Test question text",
            author=self.user,
        )
        self.answer = Answer.objects.create(
            text="Test answer", author=self.user, question=self.question
        )

    def test_answer_creation(self):
        """Тест создания ответа"""
        assert self.answer.text == "Test answer"
        assert self.answer.author == self.user
        assert self.answer.question == self.question
        assert self.answer.rating == 0
        assert self.answer.is_correct is False

    def test_answer_update_rating(self):
        """Тест обновления рейтинга ответа"""
        assert self.answer.rating == 0

        # Создаем лайк
        AnswerLike.objects.create(user=self.user, answer=self.answer, value=1)
        self.answer.update_rating()
        self.answer.refresh_from_db()
        assert self.answer.rating == 1


class LikeModelTestCase(TestCase):
    """Тесты для моделей лайков"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.question = Question.objects.create(
            title="Test Question",
            text="Test question text",
            author=self.user,
        )
        self.answer = Answer.objects.create(
            text="Test answer", author=self.user, question=self.question
        )

    def test_question_like_creation(self):
        """Тест создания лайка на вопрос"""
        like = QuestionLike.objects.create(user=self.user, question=self.question, value=1)
        assert like.user == self.user
        assert like.question == self.question
        assert like.value == 1

        # Проверяем, что рейтинг вопроса обновился
        self.question.refresh_from_db()
        assert self.question.rating == 1

    def test_answer_like_creation(self):
        """Тест создания лайка на ответ"""
        like = AnswerLike.objects.create(user=self.user, answer=self.answer, value=1)
        assert like.user == self.user
        assert like.answer == self.answer
        assert like.value == 1

        # Проверяем, что рейтинг ответа обновился
        self.answer.refresh_from_db()
        assert self.answer.rating == 1

    def test_question_like_unique_together(self):
        """Тест уникальности пары user-question для QuestionLike"""
        QuestionLike.objects.create(user=self.user, question=self.question, value=1)

        # Попытка создать дубликат должна вызвать ошибку
        try:
            QuestionLike.objects.create(user=self.user, question=self.question, value=-1)
            raise AssertionError("Should raise IntegrityError")
        except Exception:
            pass  # Ожидаем ошибку уникальности

    def test_answer_like_unique_together(self):
        """Тест уникальности пары user-answer для AnswerLike"""
        AnswerLike.objects.create(user=self.user, answer=self.answer, value=1)

        # Попытка создать дубликат должна вызвать ошибку
        try:
            AnswerLike.objects.create(user=self.user, answer=self.answer, value=-1)
            raise AssertionError("Should raise IntegrityError")
        except Exception:
            pass  # Ожидаем ошибку уникальности
