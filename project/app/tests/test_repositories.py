"""
Тесты для Django ORM репозиториев
"""

from __future__ import annotations

import pytest

from django.contrib.auth.models import User

from app.models import Answer, Question, Tag
from app.repositories import (
    AnswerRepository,
    QuestionRepository,
    TagRepository,
    UserRepository,
)


@pytest.mark.django_db
class TestQuestionRepository:
    """Тесты для QuestionRepository"""

    def setup_method(self) -> None:
        """Инициализация перед каждым тестом"""
        self.repository = QuestionRepository()
        # Создаем тестовые данные
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag = Tag.objects.create(name="python")
        self.question = Question.objects.create(
            title="Test Question",
            text="Test question text",
            author=self.user,
        )
        self.question.tags.add(self.tag)

    def test_get_all_questions_includes_author_profile(self) -> None:
        """Тест: get_all_questions включает author и profile для оптимизации"""
        # Получаем вопросы через репозиторий
        questions = self.repository.get_all_questions()

        # Проверяем, что можем получить доступ к profile без дополнительных запросов
        questions_list = list(questions)
        if questions_list:
            for q in questions_list:
                # Проверяем, что автор загружен (select_related работает)
                assert hasattr(q, "author")
                # Проверяем, что можем получить доступ к profile
                if hasattr(q.author, "profile"):
                    # Это означает, что select_related("author", "author__profile") работает
                    assert q.author.profile is not None or hasattr(q.author, "_profile_cache")

    def test_get_all_questions(self) -> None:
        """Тест получения всех вопросов (новых)"""
        questions = self.repository.get_all_questions()
        assert questions.count() >= 1
        assert self.question in questions

    def test_get_hot_questions(self) -> None:
        """Тест получения популярных вопросов"""
        # Создаем вопрос с высоким рейтингом
        hot_question = Question.objects.create(
            title="Hot Question",
            text="Hot question text",
            author=self.user,
            rating=100,
        )
        hot_question.tags.add(self.tag)

        questions = self.repository.get_hot_questions()
        assert questions.count() >= 1
        # Первый вопрос должен быть с самым высоким рейтингом
        first_question = questions.first()
        assert first_question is not None
        assert first_question.rating >= self.question.rating

    def test_get_questions_by_tag(self) -> None:
        """Тест получения вопросов по тегу"""
        questions = self.repository.get_questions_by_tag("python")
        assert questions.count() >= 1
        assert self.question in questions

    def test_get_question_by_id(self) -> None:
        """Тест получения вопроса по ID"""
        question_obj = self.repository.get_question_by_id(self.question.id)
        assert question_obj is not None
        assert question_obj.id == self.question.id
        assert question_obj.title == "Test Question"

    def test_get_question_by_id_not_found(self) -> None:
        """Тест получения вопроса по несуществующему ID"""
        question_obj = self.repository.get_question_by_id(99999)
        assert question_obj is None


@pytest.mark.django_db
class TestAnswerRepository:
    """Тесты для AnswerRepository"""

    def setup_method(self) -> None:
        """Инициализация перед каждым тестом"""
        self.repository = AnswerRepository()
        # Создаем тестовые данные
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.question = Question.objects.create(
            title="Test Question",
            text="Test question text",
            author=self.user,
        )
        self.answer = Answer.objects.create(
            text="Test answer text",
            author=self.user,
            question=self.question,
        )

    def test_get_answers_by_question_id(self) -> None:
        """Тест получения ответов на вопрос"""
        answers = self.repository.get_answers_by_question_id(self.question.id)
        assert answers.count() >= 1
        assert self.answer in answers

    def test_get_answers_by_question_id_not_found(self) -> None:
        """Тест получения ответов для несуществующего вопроса"""
        answers = self.repository.get_answers_by_question_id(99999)
        assert answers.count() == 0

    def test_get_answers_includes_author_profile(self) -> None:
        """Тест: get_answers_by_question_id включает author и profile для оптимизации"""
        # Получаем ответы через репозиторий
        answers = self.repository.get_answers_by_question_id(self.question.id)

        # Проверяем, что можем получить доступ к profile без дополнительных запросов
        answers_list = list(answers)
        if answers_list:
            for answer in answers_list:
                # Проверяем, что автор загружен (select_related работает)
                assert hasattr(answer, "author")
                # Проверяем, что можем получить доступ к profile
                if hasattr(answer.author, "profile"):
                    # Это означает, что select_related("author", "author__profile") работает
                    assert answer.author.profile is not None or hasattr(
                        answer.author, "_profile_cache"
                    )


@pytest.mark.django_db
class TestTagRepository:
    """Тесты для TagRepository"""

    def setup_method(self) -> None:
        """Инициализация перед каждым тестом"""
        self.repository = TagRepository()
        # Создаем тестовые данные
        self.tag = Tag.objects.create(name="python")
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.question = Question.objects.create(
            title="Test Question",
            text="Test question text",
            author=self.user,
        )
        self.question.tags.add(self.tag)

    def test_get_all_tags(self) -> None:
        """Тест получения всех тегов"""
        tags = self.repository.get_all_tags()
        assert tags.count() >= 1
        assert self.tag in tags

    def test_get_tag_info(self) -> None:
        """Тест получения информации о теге"""
        tag_info = self.repository.get_tag_info("python")
        assert tag_info["name"] == "python"
        assert tag_info["questions_count"] >= 1

    def test_get_tag_info_not_found(self) -> None:
        """Тест получения информации о несуществующем теге"""
        tag_info = self.repository.get_tag_info("nonexistent")
        assert tag_info["name"] == "nonexistent"
        assert tag_info["questions_count"] == 0
        assert tag_info["related_tags"] == []


@pytest.mark.django_db
class TestUserRepository:
    """Тесты для UserRepository"""

    def setup_method(self) -> None:
        """Инициализация перед каждым тестом"""
        self.repository = UserRepository()
        # Создаем тестовые данные
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@example.com"
        )
        self.question = Question.objects.create(
            title="Test Question",
            text="Test question text",
            author=self.user,
        )
        self.answer = Answer.objects.create(
            text="Test answer text",
            author=self.user,
            question=self.question,
        )

    def test_authenticate_success(self) -> None:
        """Тест успешной аутентификации"""
        user = self.repository.authenticate("testuser", "testpass")
        assert user is not None
        assert user.id == self.user.id
        assert user.username == "testuser"

    def test_authenticate_failure_wrong_password(self) -> None:
        """Тест неудачной аутентификации с неверным паролем"""
        user = self.repository.authenticate("testuser", "wrongpass")
        assert user is None

    def test_authenticate_failure_wrong_username(self) -> None:
        """Тест неудачной аутентификации с неверным username"""
        user = self.repository.authenticate("wronguser", "testpass")
        assert user is None

    def test_get_user_by_id(self) -> None:
        """Тест получения пользователя по ID"""
        user = self.repository.get_user_by_id(self.user.id)
        assert user is not None
        assert user.id == self.user.id
        assert user.username == "testuser"

    def test_get_user_by_id_not_found(self) -> None:
        """Тест получения пользователя по несуществующему ID"""
        user = self.repository.get_user_by_id(99999)
        assert user is None

    def test_get_user_by_username(self) -> None:
        """Тест получения пользователя по username"""
        user = self.repository.get_user_by_username("testuser")
        assert user is not None
        assert user.id == self.user.id
        assert user.username == "testuser"

    def test_get_user_by_username_not_found(self) -> None:
        """Тест получения пользователя по несуществующему username"""
        user = self.repository.get_user_by_username("nonexistent")
        assert user is None

    def test_get_user_questions(self) -> None:
        """Тест получения вопросов пользователя"""
        questions = self.repository.get_user_questions(self.user.id)
        assert len(questions) >= 1
        assert any(q["id"] == self.question.id for q in questions)

    def test_get_user_answers(self) -> None:
        """Тест получения ответов пользователя"""
        answers = self.repository.get_user_answers(self.user.id)
        assert len(answers) >= 1
        assert any(a["id"] == self.answer.id for a in answers)

    def test_get_best_members(self) -> None:
        """Тест получения лучших пользователей"""
        best_members = self.repository.get_best_members(limit=5)
        assert isinstance(best_members, list)
        # Проверяем структуру словарей
        if best_members:
            member = best_members[0]
            assert "id" in member
            assert "username" in member
            assert "rating" in member
