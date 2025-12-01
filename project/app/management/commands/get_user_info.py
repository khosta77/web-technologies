"""
Management command для получения информации о пользователе по ID профиля

Использование:
    python manage.py get_user_info <user_id>

Пример:
    python manage.py get_user_info 171
    python manage.py get_user_info 1
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Команда для получения информации о пользователе по ID"""

    help = "Получает информацию о пользователе (username, email) по ID профиля из URL"

    def add_arguments(self, parser: object) -> None:
        from argparse import ArgumentParser

        if isinstance(parser, ArgumentParser):
            parser.add_argument(
                "user_id",
                type=int,
                help="ID пользователя (из URL: /profile/<user_id>/)",
            )

    def handle(self, *args: object, **options: dict[str, object]) -> None:
        user_id: int = int(str(options["user_id"]))

        try:
            user = User.objects.get(id=user_id)

            self.stdout.write(self.style.SUCCESS("=" * 60))
            self.stdout.write(self.style.SUCCESS("ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ"))
            self.stdout.write(self.style.SUCCESS("=" * 60))
            self.stdout.write(f"ID: {user.id}")
            self.stdout.write(f"Username: {user.username}")
            self.stdout.write(f"Email: {user.email}")
            self.stdout.write(f"URL профиля: http://127.0.0.1:8000/profile/{user.id}/")
            self.stdout.write("")

            # Проверяем, является ли пользователь тестовым (созданным через fill_db)
            # Для тестовых пользователей пароль обычно "12345"
            self.stdout.write(self.style.WARNING("=" * 60))
            self.stdout.write(self.style.WARNING("ДАННЫЕ ДЛЯ ВХОДА"))
            self.stdout.write(self.style.WARNING("=" * 60))

            # Проверяем, может ли пользователь войти с стандартным тестовым паролем
            from django.contrib.auth import authenticate

            test_password = "12345"
            authenticated_user = authenticate(username=user.username, password=test_password)

            if authenticated_user:
                self.stdout.write(self.style.SUCCESS(f"Логин: {user.username}"))
                self.stdout.write(self.style.SUCCESS(f"Пароль: {test_password}"))
                self.stdout.write("")
                self.stdout.write(self.style.SUCCESS("✓ Пароль подтвержден"))
            else:
                self.stdout.write(self.style.ERROR(f"Логин: {user.username}"))
                self.stdout.write(self.style.ERROR("Пароль: неизвестен (не стандартный тестовый)"))
                self.stdout.write("")
                self.stdout.write(
                    self.style.WARNING("Попробуйте стандартный тестовый пароль: 12345")
                )
                self.stdout.write(self.style.WARNING("Или сбросьте пароль командой:"))
                self.stdout.write(f"  python manage.py changepassword {user.username}")

            # Дополнительная информация
            if hasattr(user, "profile"):
                self.stdout.write("")
                self.stdout.write(self.style.SUCCESS("=" * 60))
                self.stdout.write(self.style.SUCCESS("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ"))
                self.stdout.write(self.style.SUCCESS("=" * 60))
                self.stdout.write(f"Рейтинг: {user.profile.get_rating()}")
                self.stdout.write(f"Вопросов: {user.questions.count()}")
                self.stdout.write(f"Ответов: {user.answers.count()}")
                if user.profile.avatar:
                    self.stdout.write(f"Аватар: {user.profile.avatar.file.name}")

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("=" * 60))

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Пользователь с ID {user_id} не найден в базе данных.")
            )
            self.stdout.write(
                self.style.WARNING("Используйте команду для получения списка пользователей:")
            )
            shell_command = (
                '  python manage.py shell -c "from django.contrib.auth.models import User; '
                "[print(f'{u.id}: {u.username}') for u in User.objects.all()]\""
            )
            self.stdout.write(shell_command)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
