"""
Формы Django для приложения AskPupkin
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


if TYPE_CHECKING:
    from django.contrib.auth.models import User as UserType


class LoginForm(AuthenticationForm):
    """Форма авторизации на основе AuthenticationForm"""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        # Кастомизация виджетов
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter your login here"
        })
        self.fields["username"].label = "Login"
        self.fields["password"].widget.attrs.update({
            "class": "form-control"
        })


class SignupForm(UserCreationForm):
    """
    Форма регистрации на основе UserCreationForm

    Примеры использования с гибкой настройкой валидации пароля:

    1. Простой пароль (минимум 2 символа):
       form = SignupForm(password_min_length=2)

    2. Сложный пароль (минимум 12 символов):
       form = SignupForm(password_min_length=12)

    3. Без кастомной валидации (используются стандартные валидаторы Django):
       form = SignupForm(password_min_length=None)

    4. С кастомными валидаторами (дополнительно к минимальной длине):
       from django.contrib.auth.password_validation import (
           MinimumLengthValidator,
           CommonPasswordValidator
       )
       form = SignupForm(
           password_min_length=8,
           password_validators=[
               MinimumLengthValidator(min_length=8),
               CommonPasswordValidator()
           ]
       )
    """

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    avatar = forms.ImageField(
        label="Upload avatar",
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "username": "Login",
        }

    def __init__(
        self,
        *args: object,
        password_min_length: int | None = 2,
        password_validators: list | None = None,
        **kwargs: object
    ) -> None:
        """
        Инициализация формы с настройками валидации пароля

        Args:
            password_min_length: Минимальная длина пароля (по умолчанию 2)
            password_validators: Список кастомных валидаторов пароля (по умолчанию None)
        """
        super().__init__(*args, **kwargs)
        # Кастомизация виджетов для паролей
        self.fields["password1"].widget.attrs.update({
            "class": "form-control"
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control"
        })
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Repeat password"

        # Гибкая настройка валидации пароля
        # Сохраняем параметры для использования в clean_password2
        self._password_min_length = password_min_length
        self._password_validators = password_validators

        if password_min_length is not None:
            # Устанавливаем минимальную длину для полей
            self.fields["password1"].min_length = password_min_length
            self.fields["password2"].min_length = password_min_length

            # ВАЖНО: Отключаем стандартные валидаторы Django, если указана кастомная длина
            # UserCreationForm применяет валидаторы из AUTH_PASSWORD_VALIDATORS,
            # которые проверяют минимальную длину (по умолчанию 8 символов)
            self.password_validators = []  # Пустой список отключает стандартные валидаторы

    def _post_clean(self) -> None:
        """Переопределяем _post_clean для отключения стандартной валидации при кастомной длине"""
        # Если указана кастомная минимальная длина, пропускаем стандартную валидацию паролей
        if self._password_min_length is not None:
            # Вызываем только базовую очистку ModelForm без валидации паролей из SetPasswordMixin
            # Это обходит стандартную валидацию паролей Django
            from django.forms import ModelForm
            ModelForm._post_clean(self)
        else:
            # Если кастомная длина не указана, используем стандартную валидацию
            super()._post_clean()

    def clean_password2(self) -> str:
        """Валидация пароля с учетом кастомных настроек"""
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data.get("password2", "")

        # Сначала проверяем совпадение паролей
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")

        # Если кастомная минимальная длина указана, применяем только её
        if self._password_min_length is not None:
            if len(password1) < self._password_min_length:
                raise ValidationError(
                    f"Пароль должен содержать минимум {self._password_min_length} символов."
                )

            # Если указаны кастомные валидаторы, применяем их
            if self._password_validators:
                from django.contrib.auth import password_validation
                user = self.instance if hasattr(self, "instance") and self.instance else None
                password_validation.validate_password(
                    password1, user, password_validators=self._password_validators
                )

            # Если кастомная длина указана, не применяем стандартные валидаторы Django
            # Просто возвращаем password2
            return password2

        # Если кастомная длина не указана, используем стандартную валидацию Django
        # UserCreationForm использует password_validation через SetPasswordMixin
        from django.contrib.auth import password_validation

        # Для нового пользователя instance может быть None
        user = self.instance if hasattr(self, "instance") and self.instance else None

        # Применяем кастомные валидаторы, если указаны, иначе стандартные
        validators = self._password_validators if self._password_validators else None
        password_validation.validate_password(password1, user, password_validators=validators)

        return password2

    def clean_email(self) -> str:
        """Проверка уникальности email"""
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError("Это поле обязательно для заполнения")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return str(email)


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
