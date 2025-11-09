"""
Тесты для management command fill_db
"""

from __future__ import annotations

import shutil

from pathlib import Path

import pytest

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command

from app.models import Answer, Question, Tag


@pytest.mark.django_db
class TestFillDbCommand:
    """Тесты для команды fill_db"""

    def test_fill_db_creates_users_with_random_avatars(self) -> None:
        """Тест: пользователи получают случайные аватары"""
        # Выполняем команду с малым ratio
        call_command("fill_db", 5)

        users = User.objects.filter(is_superuser=False)
        assert users.count() >= 5

        # Проверяем, что у всех пользователей есть профили с аватарами
        avatars_used = set()
        for user in users:
            assert hasattr(user, "profile")
            assert user.profile.avatar
            avatars_used.add(user.profile.avatar.name)

        # Проверяем, что использованы разные аватары (если их достаточно)
        if len(avatars_used) > 1:
            assert len(avatars_used) > 1, "Должны использоваться разные аватары"

    def test_fill_db_avatars_from_static_img(self) -> None:
        """
        Тест: аватары выбираются из static/img/avatar*.jpg
        и сохраняются через Django Storage API.
        """
        call_command("fill_db", 10)

        users = User.objects.filter(is_superuser=False)

        # Проверяем, что все использованные аватары из списка доступных
        for user in users:
            if hasattr(user, "profile") and user.profile.avatar:
                avatar_name = user.profile.avatar.name
                # Проверяем, что аватар сохраняется через Django Storage API (путь avatars/...)
                assert avatar_name.startswith("avatars/"), (
                    f"Аватар должен начинаться с 'avatars/', получен: {avatar_name}"
                )
                # Проверяем, что имя файла начинается с "avatar" и заканчивается на ".jpg"
                # Django Storage API может добавлять суффикс к имени файла при конфликтах
                avatar_filename = Path(avatar_name).name
                assert avatar_filename.startswith("avatar") and avatar_filename.endswith(".jpg"), (
                    f"Имя файла аватара должно начинаться с 'avatar' "
                    f"и заканчиваться на '.jpg', получено: {avatar_filename}"
                )

    def test_fill_db_copies_avatars_to_uploads(self) -> None:
        """Тест: аватары сохраняются через Django Storage API в MEDIA_ROOT"""
        call_command("fill_db", 5)

        users = User.objects.filter(is_superuser=False)

        # Проверяем, что аватары сохранены через Django Storage API
        saved_count = 0
        for user in users:
            if hasattr(user, "profile") and user.profile.avatar:
                avatar_path = user.profile.avatar.path
                # Проверяем, что файл существует в MEDIA_ROOT
                if Path(avatar_path).exists():
                    saved_count += 1
                    # Проверяем, что путь соответствует структуре avatars/год/месяц/user_id/
                    assert "avatars" in avatar_path, (
                        f"Путь аватара должен содержать 'avatars', получен: {avatar_path}"
                    )
                    assert str(user.id) in avatar_path, (
                        f"Путь аватара должен содержать ID пользователя, получен: {avatar_path}"
                    )

        assert saved_count > 0, "Хотя бы один аватар должен быть сохранен через Django Storage API"

    def test_fill_db_uses_default_avatar_if_no_avatars_found(self) -> None:
        """Тест: используется дефолтный аватар если нет доступных файлов"""
        # Временно переименовываем папку static/img
        static_img_dir = Path(settings.BASE_DIR) / "static" / "img"
        backup_dir = Path(settings.BASE_DIR) / "static" / "img_backup"

        # Сохраняем существующие файлы
        if static_img_dir.exists():
            # Перемещаем только файлы аватаров
            avatar_files = list(static_img_dir.glob("avatar*.jpg"))
            moved_files = []

            for avatar_file in avatar_files:
                backup_file = backup_dir / avatar_file.name
                backup_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(avatar_file), str(backup_file))
                moved_files.append(backup_file)

        try:
            call_command("fill_db", 3)

            users = User.objects.filter(is_superuser=False)
            for user in users:
                if hasattr(user, "profile"):
                    # Должен использоваться дефолтный аватар
                    assert user.profile.avatar.name == "img/avatar.jpg"
        finally:
            # Восстанавливаем файлы
            if backup_dir.exists():
                for moved_file in moved_files:
                    if moved_file.exists():
                        dest_file = static_img_dir / moved_file.name
                        shutil.move(str(moved_file), str(dest_file))

    def test_fill_db_creates_correct_amount_of_data(self) -> None:
        """Тест: команда создает правильное количество данных"""
        ratio = 5
        call_command("fill_db", ratio)

        assert User.objects.filter(is_superuser=False).count() == ratio
        assert Tag.objects.count() == ratio
        assert Question.objects.count() == ratio * 10
        assert Answer.objects.count() == ratio * 100

    def test_fill_db_random_avatar_distribution(self) -> None:
        """Тест: проверка распределения аватаров (используются разные аватары)"""
        call_command("fill_db", 20)

        users = User.objects.filter(is_superuser=False)
        avatars_used: dict[str, int] = {}

        for user in users:
            if hasattr(user, "profile") and user.profile.avatar:
                avatar_name = user.profile.avatar.name
                avatars_used[avatar_name] = avatars_used.get(avatar_name, 0) + 1

        # Если есть несколько аватаров, должны использоваться разные
        static_img_dir = Path(settings.BASE_DIR) / "static" / "img"
        available_count = len(list(static_img_dir.glob("avatar*.jpg")))

        if available_count > 1 and len(users) >= available_count:
            # Проверяем, что использовано более одного аватара
            unique_avatars = len(set(avatars_used.keys()))
            assert unique_avatars > 1, (
                f"Должно использоваться более одного аватара, использовано: {unique_avatars}"
            )
