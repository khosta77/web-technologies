"""
Management command для вывода списка всех пользователей

Использование:
    python manage.py list_users

Пример:
    python manage.py list_users
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Команда для вывода списка всех пользователей"""

    help = "Выводит список всех пользователей в формате ID: username"

    def handle(self, *args: object, **options: dict[str, object]) -> None:
        """Обработка команды"""
        users = User.objects.all().order_by("id")

        if not users.exists():
            self.stdout.write(self.style.WARNING("В базе данных нет пользователей."))
            return

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("СПИСОК ПОЛЬЗОВАТЕЛЕЙ"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")

        for user in users:
            self.stdout.write(f"{user.id}: {user.username}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS(f"Всего пользователей: {users.count()}"))
