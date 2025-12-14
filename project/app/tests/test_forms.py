"""
Тесты для форм Django
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase

from app.forms import (
    EditProfileForm,
    LikeAnswerForm,
    LikeQuestionForm,
    MarkCorrectAnswerForm,
    SignupForm,
)


class SignupFormTestCase(TestCase):
    """Тесты для формы регистрации SignupForm"""

    def test_signup_form_with_custom_min_length_2(self):
        """Тест: форма принимает пароль длиной 2 символа при password_min_length=2"""
        form = SignupForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "12",
                "password2": "12",
            },
            password_min_length=2,
        )
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_signup_form_with_custom_min_length_2_rejects_short(self):
        """Тест: форма отклоняет пароль длиной 1 символ при password_min_length=2"""
        form = SignupForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "1",
                "password2": "1",
            },
            password_min_length=2,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_signup_form_with_custom_min_length_12(self):
        """Тест: форма принимает пароль длиной 12 символов при password_min_length=12"""
        form = SignupForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "123456789012",
                "password2": "123456789012",
            },
            password_min_length=12,
        )
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_signup_form_with_custom_min_length_12_rejects_short(self):
        """Тест: форма отклоняет пароль длиной 6 символов при password_min_length=12"""
        form = SignupForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "123456",
                "password2": "123456",
            },
            password_min_length=12,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
        # Проверяем, что ошибка связана с минимальной длиной
        error_text = str(form.errors["password2"])
        self.assertIn("минимум 12", error_text)

    def test_signup_form_without_custom_length_uses_default_validators(self):
        """Тест: форма использует стандартные валидаторы Django при password_min_length=None"""
        form = SignupForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "12",  # Слишком короткий для стандартных валидаторов
                "password2": "12",
            },
            password_min_length=None,
        )
        # Стандартные валидаторы Django требуют минимум 8 символов
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_signup_form_password_mismatch(self):
        """Тест: форма отклоняет несовпадающие пароли"""
        form = SignupForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "12345",
                "password2": "54321",
            },
            password_min_length=2,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
        error_text = str(form.errors["password2"])
        self.assertIn("не совпадают", error_text)

    def test_signup_form_email_validation(self):
        """Тест: форма проверяет уникальность email"""
        # Создаем пользователя с существующим email
        User.objects.create_user(username="existing", email="test@example.com", password="pass123")

        form = SignupForm(
            {
                "username": "newuser",
                "email": "test@example.com",  # Дублирующийся email
                "password1": "12345",
                "password2": "12345",
            },
            password_min_length=2,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_signup_form_username_validation(self):
        """Тест: форма проверяет уникальность username"""
        # Создаем пользователя с существующим username
        User.objects.create_user(username="testuser", email="old@example.com", password="pass123")

        form = SignupForm(
            {
                "username": "testuser",  # Дублирующийся username
                "email": "new@example.com",
                "password1": "12345",
                "password2": "12345",
            },
            password_min_length=2,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_signup_form_valid_data(self):
        """Тест: форма принимает валидные данные"""
        form = SignupForm(
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "12345",
                "password2": "12345",
            },
            password_min_length=2,
        )
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        user = form.save(commit=False)
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "new@example.com")


class LikeQuestionFormTestCase(TestCase):
    """Тесты для формы LikeQuestionForm"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        from app.models import Question

        self.question = Question.objects.create(
            title="Test Question", text="Test text", author=self.user
        )

    def test_like_question_form_valid(self):
        """Тест: форма принимает валидные данные"""
        form = LikeQuestionForm({"question_id": self.question.id, "value": 1}, user=self.user)
        self.assertTrue(form.is_valid())

    def test_like_question_form_invalid_value(self):
        """Тест: форма отклоняет невалидное значение"""
        form = LikeQuestionForm({"question_id": self.question.id, "value": 2}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("value", form.errors)

    def test_like_question_form_nonexistent_question(self):
        """Тест: форма отклоняет несуществующий вопрос"""
        form = LikeQuestionForm({"question_id": 99999, "value": 1}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("question_id", form.errors)

    def test_like_question_form_save_creates_like(self):
        """Тест: save создает лайк"""
        form = LikeQuestionForm({"question_id": self.question.id, "value": 1}, user=self.user)
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertIn("rating", result)
        self.assertIn("removed", result)

    def test_like_question_form_save_removes_duplicate(self):
        """Тест: save удаляет дубликат лайка"""
        from app.models import QuestionLike

        # Создаем лайк
        QuestionLike.objects.create(user=self.user, question=self.question, value=1)
        self.question.refresh_from_db()

        # Пытаемся создать тот же лайк
        form = LikeQuestionForm({"question_id": self.question.id, "value": 1}, user=self.user)
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertTrue(result["removed"])

    def test_like_question_form_save_updates_like(self):
        """Тест: save обновляет существующий лайк"""
        from app.models import QuestionLike

        # Создаем лайк
        QuestionLike.objects.create(user=self.user, question=self.question, value=1)
        self.question.refresh_from_db()

        # Меняем на дизлайк
        form = LikeQuestionForm({"question_id": self.question.id, "value": -1}, user=self.user)
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertFalse(result["removed"])

    def test_like_question_form_save_requires_authentication(self):
        """Тест: save требует аутентификации"""
        form = LikeQuestionForm({"question_id": self.question.id, "value": 1}, user=None)
        self.assertTrue(form.is_valid())
        with self.assertRaises(ValueError):
            form.save()


class LikeAnswerFormTestCase(TestCase):
    """Тесты для формы LikeAnswerForm"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        from app.models import Answer, Question

        self.question = Question.objects.create(
            title="Test Question", text="Test text", author=self.user
        )
        self.answer = Answer.objects.create(
            text="Test answer", author=self.user, question=self.question
        )

    def test_like_answer_form_valid(self):
        """Тест: форма принимает валидные данные"""
        form = LikeAnswerForm({"answer_id": self.answer.id, "value": 1}, user=self.user)
        self.assertTrue(form.is_valid())

    def test_like_answer_form_invalid_value(self):
        """Тест: форма отклоняет невалидное значение"""
        form = LikeAnswerForm({"answer_id": self.answer.id, "value": 0}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("value", form.errors)

    def test_like_answer_form_nonexistent_answer(self):
        """Тест: форма отклоняет несуществующий ответ"""
        form = LikeAnswerForm({"answer_id": 99999, "value": 1}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("answer_id", form.errors)

    def test_like_answer_form_save_creates_like(self):
        """Тест: save создает лайк"""
        form = LikeAnswerForm({"answer_id": self.answer.id, "value": 1}, user=self.user)
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertIn("rating", result)
        self.assertIn("removed", result)

    def test_like_answer_form_save_removes_duplicate(self):
        """Тест: save удаляет дубликат лайка"""
        from app.models import AnswerLike

        AnswerLike.objects.create(user=self.user, answer=self.answer, value=1)
        self.answer.refresh_from_db()

        form = LikeAnswerForm({"answer_id": self.answer.id, "value": 1}, user=self.user)
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertTrue(result["removed"])

    def test_like_answer_form_save_requires_authentication(self):
        """Тест: save требует аутентификации"""
        form = LikeAnswerForm({"answer_id": self.answer.id, "value": 1}, user=None)
        self.assertTrue(form.is_valid())
        with self.assertRaises(ValueError):
            form.save()


class MarkCorrectAnswerFormTestCase(TestCase):
    """Тесты для формы MarkCorrectAnswerForm"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        from app.models import Answer, Question

        self.question = Question.objects.create(
            title="Test Question", text="Test text", author=self.user
        )
        self.answer = Answer.objects.create(
            text="Test answer", author=self.other_user, question=self.question
        )

    def test_mark_correct_answer_form_valid(self):
        """Тест: форма принимает валидные данные"""
        form = MarkCorrectAnswerForm(
            {"question_id": self.question.id, "answer_id": self.answer.id, "is_correct": True},
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_mark_correct_answer_form_nonexistent_question(self):
        """Тест: форма отклоняет несуществующий вопрос"""
        form = MarkCorrectAnswerForm(
            {"question_id": 99999, "answer_id": self.answer.id, "is_correct": True},
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("question_id", form.errors)

    def test_mark_correct_answer_form_nonexistent_answer(self):
        """Тест: форма отклоняет несуществующий ответ"""
        form = MarkCorrectAnswerForm(
            {"question_id": self.question.id, "answer_id": 99999, "is_correct": True},
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("answer_id", form.errors)

    def test_mark_correct_answer_form_wrong_author(self):
        """Тест: форма отклоняет отметку от неавтора вопроса"""
        form = MarkCorrectAnswerForm(
            {
                "question_id": self.question.id,
                "answer_id": self.answer.id,
                "is_correct": True,
            },
            user=self.other_user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("question_id", form.errors)

    def test_mark_correct_answer_form_save_marks_correct(self):
        """Тест: save отмечает ответ как правильный"""
        form = MarkCorrectAnswerForm(
            {"question_id": self.question.id, "answer_id": self.answer.id, "is_correct": True},
            user=self.user,
        )
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertTrue(result["success"])
        self.assertTrue(result["is_correct"])
        self.answer.refresh_from_db()
        self.assertTrue(self.answer.is_correct)

    def test_mark_correct_answer_form_save_unmarks_correct(self):
        """Тест: save снимает отметку правильного ответа"""
        self.answer.is_correct = True
        self.answer.save()

        form = MarkCorrectAnswerForm(
            {"question_id": self.question.id, "answer_id": self.answer.id, "is_correct": False},
            user=self.user,
        )
        self.assertTrue(form.is_valid())
        result = form.save()
        self.assertTrue(result["success"])
        self.assertFalse(result["is_correct"])
        self.answer.refresh_from_db()
        self.assertFalse(self.answer.is_correct)

    def test_mark_correct_answer_form_save_resets_other_answers(self):
        """Тест: save сбрасывает другие правильные ответы"""
        from app.models import Answer

        answer2 = Answer.objects.create(
            text="Another answer", author=self.other_user, question=self.question, is_correct=True
        )

        form = MarkCorrectAnswerForm(
            {"question_id": self.question.id, "answer_id": self.answer.id, "is_correct": True},
            user=self.user,
        )
        self.assertTrue(form.is_valid())
        form.save()

        answer2.refresh_from_db()
        self.assertFalse(answer2.is_correct)
        self.answer.refresh_from_db()
        self.assertTrue(self.answer.is_correct)


class EditProfileFormTestCase(TestCase):
    """Тесты для формы EditProfileForm"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_edit_profile_form_valid(self):
        """Тест: форма принимает валидные данные"""
        form = EditProfileForm(
            {"username": "newusername", "email": "new@example.com"},
            instance=self.user,
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_edit_profile_form_duplicate_username(self):
        """Тест: форма отклоняет дублирующийся username"""
        User.objects.create_user(
            username="existing", email="existing@example.com", password="pass123"
        )

        form = EditProfileForm(
            {"username": "existing", "email": "new@example.com"},
            instance=self.user,
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_edit_profile_form_duplicate_email(self):
        """Тест: форма отклоняет дублирующийся email"""
        User.objects.create_user(
            username="existing", email="existing@example.com", password="pass123"
        )

        form = EditProfileForm(
            {"username": "newusername", "email": "existing@example.com"},
            instance=self.user,
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_edit_profile_form_same_username_allowed(self):
        """Тест: форма разрешает тот же username"""
        form = EditProfileForm(
            {"username": "testuser", "email": "new@example.com"},
            instance=self.user,
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_edit_profile_form_password_change_valid(self):
        """Тест: форма принимает валидную смену пароля"""
        form = EditProfileForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "current_password": "testpass123",
                "new_password": "newpass123",
                "confirm_password": "newpass123",
            },
            instance=self.user,
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_edit_profile_form_password_change_wrong_current(self):
        """Тест: форма отклоняет смену пароля с неверным текущим"""
        form = EditProfileForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "current_password": "wrongpass",
                "new_password": "newpass123",
                "confirm_password": "newpass123",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("current_password", form.errors)

    def test_edit_profile_form_password_change_mismatch(self):
        """Тест: форма отклоняет несовпадающие новые пароли"""
        form = EditProfileForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "current_password": "testpass123",
                "new_password": "newpass123",
                "confirm_password": "differentpass",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_password", form.errors)

    def test_edit_profile_form_password_change_partial(self):
        """Тест: форма отклоняет частичное заполнение полей пароля"""
        form = EditProfileForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "current_password": "testpass123",
                "new_password": "newpass123",
                # confirm_password отсутствует
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_password", form.errors)

    def test_edit_profile_form_save_updates_user(self):
        """Тест: save обновляет пользователя"""
        form = EditProfileForm(
            {"username": "newusername", "email": "new@example.com"},
            instance=self.user,
            user=self.user,
        )
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.username, "newusername")
        self.assertEqual(updated_user.email, "new@example.com")

    def test_edit_profile_form_save_changes_password(self):
        """Тест: save меняет пароль"""
        form = EditProfileForm(
            {
                "username": "testuser",
                "email": "test@example.com",
                "current_password": "testpass123",
                "new_password": "newpass123",
                "confirm_password": "newpass123",
            },
            instance=self.user,
            user=self.user,
        )
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))
