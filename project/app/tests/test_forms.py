"""
Тесты для форм Django
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase

from app.forms import SignupForm


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
        User.objects.create_user(
            username="existing", email="test@example.com", password="pass123"
        )

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
        User.objects.create_user(
            username="testuser", email="old@example.com", password="pass123"
        )

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

