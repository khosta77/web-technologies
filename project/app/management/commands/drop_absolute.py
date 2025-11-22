"""
Management command для полной очистки базы данных и миграций

Использование:
    python manage.py drop_absolute [--force]

Команда выполняет:
    1. Удаление всех данных из всех таблиц
    2. Удаление всех файлов миграций (кроме __init__.py)
    3. Удаление файла базы данных (если используется SQLite)
    4. Сброс всех миграций

ВНИМАНИЕ: Это опасная команда! Она полностью удаляет все данные и миграции.
Используйте только в режиме разработки!
"""

from __future__ import annotations

import shutil

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """Команда для полной очистки базы данных и миграций"""

    help = "Полностью очищает базу данных и удаляет все миграции"

    def add_arguments(self, parser: object) -> None:
        from argparse import ArgumentParser

        if isinstance(parser, ArgumentParser):
            parser.add_argument(
                "--force",
                action="store_true",
                help="Выполнить без подтверждения (опасно!)",
            )

    def handle(self, *args: object, **options: dict[str, object]) -> None:
        """Выполнение команды"""
        force: bool = bool(options.get("force", False))

        if not force:
            self.stdout.write(self.style.WARNING("ВНИМАНИЕ: Эта команда полностью удалит:"))
            self.stdout.write("   - Все данные из базы данных")
            self.stdout.write("   - Все файлы миграций (кроме __init__.py)")
            self.stdout.write("   - Файл базы данных (если используется SQLite)")
            self.stdout.write("")
            confirm = input("Вы уверены? Введите 'yes' для подтверждения: ")
            if confirm.lower() != "yes":
                self.stdout.write(self.style.ERROR("Операция отменена."))
                return

        self.stdout.write(self.style.WARNING("Начинаю полную очистку..."))

        # 1. Удаление всех данных из БД
        self._clear_database()

        # 2. Удаление файлов миграций
        self._remove_migrations()

        # 3. Удаление файла БД (если SQLite)
        self._remove_database_file()

        # 4. Сброс миграций
        self._reset_migrations()

        self.stdout.write(self.style.SUCCESS("Полная очистка завершена успешно!"))
        self.stdout.write("")
        self.stdout.write("Следующие шаги:")
        self.stdout.write(
            "  1. Создайте новые миграции: poetry run python manage.py makemigrations"
        )
        self.stdout.write("  2. Примените миграции: poetry run python manage.py migrate")
        self.stdout.write("  3. (Опционально) Заполните БД: poetry run python manage.py fill_db")

    def _clear_database(self) -> None:
        """Удаление всех данных из базы данных"""
        self.stdout.write("🗑️  Удаление всех данных из базы данных...")

        with connection.cursor() as cursor:
            # Получаем список всех таблиц
            if connection.vendor == "postgresql":
                cursor.execute(
                    """
                    SELECT tablename FROM pg_tables
                    WHERE schemaname = 'public'
                    """
                )
                tables = [row[0] for row in cursor.fetchall()]
            elif connection.vendor == "sqlite":
                cursor.execute(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """
                )
                tables = [row[0] for row in cursor.fetchall()]
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Неизвестный тип БД: {connection.vendor}. Пропускаю очистку данных."
                    )
                )
                return

            # Удаляем все таблицы (CASCADE удалит связанные объекты)
            if connection.vendor == "postgresql":
                # Для PostgreSQL удаляем все таблицы каскадно
                for table in tables:
                    try:
                        cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                        self.stdout.write(f"   Удалена таблица: {table}")
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"   Не удалось удалить {table}: {e}"))
            elif connection.vendor == "sqlite":
                # Для SQLite отключаем проверки внешних ключей
                cursor.execute("PRAGMA foreign_keys = OFF")
                # Удаляем все таблицы
                for table in tables:
                    try:
                        cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
                        self.stdout.write(f"   Удалена таблица: {table}")
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"   Не удалось удалить {table}: {e}"))
                cursor.execute("PRAGMA foreign_keys = ON")

            # Удаляем оставшиеся последовательности (для PostgreSQL)
            # CASCADE должен удалить их автоматически, но на всякий случай проверим
            if connection.vendor == "postgresql":
                cursor.execute(
                    """
                    SELECT sequence_name FROM information_schema.sequences
                    WHERE sequence_schema = 'public'
                    """
                )
                sequences = [row[0] for row in cursor.fetchall()]
                for seq in sequences:
                    try:
                        cursor.execute(f'DROP SEQUENCE IF EXISTS "{seq}" CASCADE')
                        self.stdout.write(f"   Удалена последовательность: {seq}")
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f"   Не удалось удалить последовательность {seq}: {e}"
                            )
                        )

        self.stdout.write(self.style.SUCCESS("   База данных очищена"))

    def _remove_migrations(self) -> None:
        """Удаление всех файлов миграций (кроме __init__.py)"""
        self.stdout.write("Удаление файлов миграций...")

        migrations_dir = Path(settings.BASE_DIR) / "app" / "migrations"

        if not migrations_dir.exists():
            self.stdout.write(self.style.WARNING("   Папка миграций не найдена"))
            return

        removed_count = 0
        for file_path in migrations_dir.iterdir():
            # Пропускаем __init__.py и __pycache__
            if file_path.name == "__init__.py" or file_path.is_dir():
                continue

            if file_path.is_file() and file_path.suffix == ".py":
                try:
                    file_path.unlink()
                    removed_count += 1
                    self.stdout.write(f"   Удален: {file_path.name}")
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"   Не удалось удалить {file_path.name}: {e}")
                    )

        # Удаляем __pycache__
        pycache_dir = migrations_dir / "__pycache__"
        if pycache_dir.exists():
            try:
                shutil.rmtree(pycache_dir)
                self.stdout.write("   Удален __pycache__")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"   ⚠ Не удалось удалить __pycache__: {e}"))

        if removed_count > 0:
            self.stdout.write(self.style.SUCCESS(f"   ✓ Удалено {removed_count} файлов миграций"))
        else:
            self.stdout.write(self.style.SUCCESS("   ✓ Файлы миграций не найдены"))

    def _remove_database_file(self) -> None:
        """Удаление файла базы данных (если используется SQLite)"""
        if connection.vendor != "sqlite":
            self.stdout.write("   Используется не SQLite, файл БД не удаляется")
            return

        self.stdout.write("🗑️  Удаление файла базы данных...")

        db_path = Path(settings.DATABASES["default"]["NAME"])

        if not db_path.exists():
            self.stdout.write(self.style.WARNING("   ⚠ Файл базы данных не найден"))
            return

        try:
            db_path.unlink()
            self.stdout.write(self.style.SUCCESS(f"   ✓ Удален файл БД: {db_path}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"   ⚠ Не удалось удалить файл БД: {e}"))

    def _reset_migrations(self) -> None:
        """Сброс всех миграций в Django"""
        self.stdout.write(" Сброс миграций в Django...")
        # Таблица django_migrations уже удалена в _clear_database,
        # поэтому здесь ничего делать не нужно
        self.stdout.write("   Таблица django_migrations уже удалена")
