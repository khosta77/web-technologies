"""
Формы Django для приложения AskPupkin
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


if TYPE_CHECKING:
    from django.contrib.auth.models import User as UserType


class LoginForm(forms.Form):
    """Форма авторизации"""

    username = forms.CharField(
        max_length=150,
        label="Login",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter your login here"}
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )


class SignupForm(forms.ModelForm):
    """Форма регистрации"""

    password = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        min_length=5,
    )
    repeat_password = forms.CharField(
        label="Repeat password",
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        min_length=5,
    )
    avatar = forms.ImageField(
        label="Upload avatar",
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
        labels = {
            "username": "Login",
            "email": "Email",
        }

    def clean_username(self) -> str:
        """Проверка уникальности username"""
        username = self.cleaned_data.get("username")
        if not username:
            raise ValidationError("Это поле обязательно для заполнения")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует")
        return str(username)

    def clean_email(self) -> str:
        """Проверка уникальности email"""
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError("Это поле обязательно для заполнения")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return str(email)

    def clean_password(self) -> str:
        """Проверка пароля"""
        password = self.cleaned_data.get("password")
        if not password:
            raise ValidationError("Это поле обязательно для заполнения")
        return str(password)

    def clean_repeat_password(self) -> str:
        """Проверка совпадения паролей"""
        password = self.cleaned_data.get("password")
        repeat_password = self.cleaned_data.get("repeat_password")
        if not repeat_password:
            raise ValidationError("Это поле обязательно для заполнения")
        if password and repeat_password and password != repeat_password:
            raise ValidationError("Пароли не совпадают")
        return str(repeat_password)


class AskQuestionForm(forms.Form):
    """Форма добавления вопроса"""

    title = forms.CharField(
        max_length=255,
        label="Title",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "maxlength": "200",
                "placeholder": "Enter question title",
            }
        ),
    )
    text = forms.CharField(
        label="Text",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": "10", "placeholder": "Enter question text"}
        ),
    )
    tags = forms.CharField(
        max_length=100,
        label="Tags",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "maxlength": "100",
                "placeholder": "Enter tags separated by commas",
            }
        ),
        help_text="Введите теги через запятую",
    )

    def clean_tags(self) -> list[str]:
        """Парсинг тегов из строки"""
        tags_str = self.cleaned_data.get("tags", "")
        if not tags_str:
            return []
        # Разделяем по запятой, убираем пробелы, фильтруем пустые
        tags_list = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        return tags_list


class AddAnswerForm(forms.Form):
    """Форма добавления ответа"""

    text = forms.CharField(
        label="Your Answer",
        widget=forms.Textarea(
            attrs={
                "class": "answer-textarea form-control",
                "placeholder": "Enter your answer here..",
            }
        ),
    )


class EditProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""

    avatar = forms.ImageField(
        label="Avatar",
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*"}),
    )
    current_password = forms.CharField(
        label="Current Password",
        required=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter your current password"}
        ),
        help_text="Введите текущий пароль для смены пароля",
    )
    new_password = forms.CharField(
        label="New Password",
        required=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter new password"}
        ),
        min_length=5,
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        required=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm new password"}
        ),
        min_length=5,
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
        labels = {
            "username": "Username",
            "email": "Email",
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Инициализация формы с текущим пользователем"""
        user = kwargs.pop("user", None)
        self.user: UserType | None = user if isinstance(user, User) else None
        super().__init__(*args, **kwargs)
        if self.user and isinstance(self.user, User):
            self.fields["username"].initial = self.user.username
            self.fields["email"].initial = self.user.email

    def clean_username(self) -> str:
        """Проверка уникальности username (кроме текущего пользователя)"""
        username = self.cleaned_data.get("username")
        if not username:
            # Если username пустой, возвращаем текущий username
            return str(self.user.username) if self.user else ""
        # Если username не изменился, не проверяем уникальность
        if self.user and username == self.user.username:
            return str(username)
        # Проверяем уникальность только если username изменился
        if self.user and User.objects.filter(username=username).exclude(id=self.user.id).exists():
            raise ValidationError("Пользователь с таким именем уже существует")
        return str(username)

    def clean_email(self) -> str:
        """Проверка уникальности email (кроме текущего пользователя)"""
        email = self.cleaned_data.get("email")
        if not email:
            # Если email пустой, возвращаем текущий email
            return str(self.user.email) if self.user else ""
        # Если email не изменился, не проверяем уникальность
        if self.user and email == self.user.email:
            return str(email)
        # Проверяем уникальность только если email изменился
        if self.user and User.objects.filter(email=email).exclude(id=self.user.id).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return str(email)

    def clean(self) -> dict[str, object]:
        """Валидация смены пароля"""
        cleaned_data: dict[str, object] = dict(super().clean())
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Если хотя бы одно поле пароля заполнено, все должны быть заполнены
        if current_password or new_password or confirm_password:
            if not current_password:
                raise ValidationError({"current_password": "Введите текущий пароль"})
            if not new_password:
                raise ValidationError({"new_password": "Введите новый пароль"})
            if not confirm_password:
                raise ValidationError({"confirm_password": "Подтвердите новый пароль"})

            # Проверка совпадения новых паролей
            if new_password and confirm_password and new_password != confirm_password:
                raise ValidationError({"confirm_password": "Новые пароли не совпадают"})

            # Проверка текущего пароля
            if self.user and not self.user.check_password(str(current_password)):
                raise ValidationError({"current_password": "Неверный текущий пароль"})

        return cleaned_data
