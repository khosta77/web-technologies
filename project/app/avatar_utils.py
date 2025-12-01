"""
Утилиты для работы с аватарами и дедупликацией файлов
"""

from __future__ import annotations

import contextlib
import hashlib
import os

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    SimpleUploadedFile,
    TemporaryUploadedFile,
    UploadedFile,
)

from app.models import AvatarFile


def ensure_avatar_directory_exists() -> None:
    """
    Создает директорию для аватаров, если она не существует
    """
    avatar_dir = Path(settings.MEDIA_ROOT) / "avatars" / "unique"
    avatar_dir.mkdir(parents=True, exist_ok=True)


def compute_file_hash(
    file: File | UploadedFile | InMemoryUploadedFile | TemporaryUploadedFile,
) -> str:
    """
    Вычисляет MD5 хеш файла

    Args:
        file: Файл для вычисления хеша

    Returns:
        str: MD5 хеш файла в виде строки
    """
    file.seek(0)  # Перемещаемся в начало файла
    hash_md5 = hashlib.md5()
    for chunk in file.chunks():
        hash_md5.update(chunk)
    file.seek(0)  # Возвращаемся в начало для дальнейшего использования
    return hash_md5.hexdigest()


def get_or_create_avatar_file(
    uploaded_file: File | UploadedFile | InMemoryUploadedFile | TemporaryUploadedFile,
) -> AvatarFile:
    """
    Получает существующий AvatarFile по хешу или создает новый

    Args:
        uploaded_file: Загруженный файл аватара

    Returns:
        AvatarFile: Существующий или созданный объект AvatarFile
    """
    file_hash = compute_file_hash(uploaded_file)

    # Убеждаемся, что директория для аватаров существует
    ensure_avatar_directory_exists()

    # Пытаемся найти существующий файл с таким хешем
    try:
        avatar_file = AvatarFile.objects.get(file_hash=file_hash)
        # Файл уже существует, увеличиваем счетчик использования
        avatar_file.usage_count += 1
        avatar_file.save(update_fields=["usage_count"])

        # ВАЖНО: Проверяем, существует ли файл физически на диске
        # Если директория была удалена, но запись осталась в БД, файл нужно восстановить
        if hasattr(avatar_file.file, "path"):
            django_path = Path(avatar_file.file.path)
            if not django_path.exists():
                # Файл отсутствует на диске, восстанавливаем его
                uploaded_file.seek(0)
                file_content = uploaded_file.read()
                uploaded_file.seek(0)

                # Убеждаемся, что родительская директория существует
                django_path.parent.mkdir(parents=True, exist_ok=True)

                # Восстанавливаем файл
                with open(django_path, "wb") as file_handle:
                    written = file_handle.write(file_content)
                    file_handle.flush()
                    with contextlib.suppress(AttributeError, OSError):
                        os.fsync(file_handle.fileno())

                # Проверяем, что файл был создан
                if not django_path.exists():
                    raise RuntimeError(
                        f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось восстановить файл по пути: {django_path}"
                    ) from None
    except AvatarFile.DoesNotExist:
        file_name = uploaded_file.name if hasattr(uploaded_file, "name") else "avatar.jpg"
        uploaded_file.seek(0)
        file_content = uploaded_file.read()
        uploaded_file.seek(0)

        file_extension = Path(file_name).suffix or ".jpg"
        unique_file_name = f"{file_hash}{file_extension}"

        content_file = ContentFile(file_content, name=unique_file_name)

        avatar_file = AvatarFile(file_hash=file_hash, usage_count=1)
        avatar_file.save()

        saved_name = avatar_file.file.save(unique_file_name, content_file, save=True)

        # КРИТИЧЕСКИ ВАЖНО: Django file.save() НЕ сохраняет файл физически
        if not hasattr(avatar_file.file, "path"):
            raise RuntimeError("avatar_file.file не имеет атрибута path") from None

        django_path = Path(avatar_file.file.path)
        django_path.parent.mkdir(parents=True, exist_ok=True)

        uploaded_file.seek(0)
        final_content = uploaded_file.read()
        uploaded_file.seek(0)

        # ВАЖНО: Сохраняем файл вручную
        with open(django_path, "wb") as file_handle:
            written = file_handle.write(final_content)
            file_handle.flush()
            with contextlib.suppress(AttributeError, OSError):
                os.fsync(file_handle.fileno())

        if not django_path.exists():
            parent_writable = (
                os.access(django_path.parent, os.W_OK) if django_path.parent.exists() else False
            )
            raise RuntimeError(
                f"КРИТИЧЕСКАЯ ОШИБКА: Файл не существует после сохранения по пути: {django_path}. "
                f"Было записано байт: {written if 'written' in locals() else 'unknown'}, "
                f"Родительская директория существует: {django_path.parent.exists()}, "
                f"Доступна для записи: {parent_writable}"
            ) from None

    return avatar_file  # type: ignore[no-any-return]


def get_default_avatar_file() -> AvatarFile | None:
    """
    Получает дефолтный аватар из static/img/avatar.jpg

    Returns:
        AvatarFile | None: AvatarFile с дефолтным аватаром или None если файл не найден
    """
    from pathlib import Path

    from django.conf import settings

    default_avatar_path = Path(settings.BASE_DIR) / "static" / "img" / "avatar.jpg"

    if not default_avatar_path.exists():
        return None

    with open(default_avatar_path, "rb") as f:
        file_content = f.read()
    file_obj = SimpleUploadedFile(
        name="avatar.jpg",
        content=file_content,
        content_type="image/jpeg",
    )
    avatar_file: AvatarFile = get_or_create_avatar_file(file_obj)
    return avatar_file
