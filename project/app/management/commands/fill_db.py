"""
Management command для наполнения базы данных тестовыми данными

Использование:
    python manage.py fill_db [ratio]

Где ratio - коэффициент для масштабирования данных:
    - ratio пользователей
    - ratio * 10 вопросов
    - ratio * 100 ответов
    - ratio тегов
    - ratio * 200 оценок (лайков)
"""

from __future__ import annotations

import hashlib
import random
import time

from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from faker import Faker
from tqdm import tqdm

from app.avatar_utils import ensure_avatar_directory_exists, get_or_create_avatar_file
from app.models import Answer, AnswerLike, Profile, Question, QuestionLike, Tag


fake = Faker("ru_RU")


class Command(BaseCommand):
    """Команда для наполнения базы данных тестовыми данными"""

    help = "Заполняет базу данных тестовыми данными согласно коэффициенту ratio"

    def add_arguments(self, parser: object) -> None:
        from argparse import ArgumentParser

        if isinstance(parser, ArgumentParser):
            parser.add_argument(
                "ratio",
                type=int,
                nargs="?",
                default=100,
                help="Коэффициент для масштабирования данных (по умолчанию 100)",
            )

    def handle(self, *args: object, **options: dict[str, object]) -> None:
        start_time = time.perf_counter()
        ratio_value = options.get("ratio", 100)
        ratio: int = int(ratio_value) if isinstance(ratio_value, (int, str)) else 100

        self.stdout.write(f"Начало наполнения базы данных с коэффициентом ratio={ratio}...")

        # Очищаем базу данных
        self.stdout.write("Очистка существующих данных...")
        AnswerLike.objects.all().delete()
        QuestionLike.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Tag.objects.all().delete()

        # Создаем теги
        tags_list = []
        tag_names = set()

        # Используем популярные теги программирования
        popular_tags = [
            "python",
            "django",
            "javascript",
            "react",
            "vue",
            "mysql",
            "postgresql",
            "docker",
            "kubernetes",
            "html",
            "css",
            "java",
            "c++",
            "web",
            "programming",
            "linux",
            "git",
            "mongodb",
            "redis",
            "api",
            "typescript",
            "nodejs",
            "flask",
            "fastapi",
            "graphql",
            "rest",
            "sql",
            "nosql",
            "aws",
            "azure",
            "gcp",
            "ci-cd",
            "testing",
            "security",
            "performance",
            "architecture",
            "microservices",
            "frontend",
            "backend",
            "devops",
        ]

        # Генерируем уникальные теги
        tags_to_create = []
        for i in tqdm(range(ratio), desc="Генерация тегов", unit="тег"):
            if i < len(popular_tags):
                tag_name = popular_tags[i]
            else:
                # Генерируем уникальный тег используя комбинации для избежания повторений
                attempts = 0
                max_attempts = 100
                while attempts < max_attempts:
                    # Используем комбинации слов и чисел для разнообразия
                    if random.random() < 0.5:
                        # Комбинация двух слов
                        word1 = fake.word().lower().replace(" ", "-")
                        word2 = fake.word().lower().replace(" ", "-")
                        tag_name = f"{word1}-{word2}"
                    else:
                        # Одно слово + случайное число
                        word = fake.word().lower().replace(" ", "-")
                        number = random.randint(1000, 9999)
                        tag_name = f"{word}-{number}"

                    if tag_name not in tag_names:
                        break
                    attempts += 1
                else:
                    # Если не удалось сгенерировать уникальный тег, используем хеш
                    base_word = fake.word().lower().replace(" ", "-")
                    hash_suffix = hashlib.md5(
                        f"{base_word}{i}{random.randint(0, 1000000)}".encode()
                    ).hexdigest()[:8]
                    tag_name = f"{base_word}-{hash_suffix}"

            tag_names.add(tag_name)
            tags_to_create.append(Tag(name=tag_name))

        tags_list = Tag.objects.bulk_create(tags_to_create)

        users_list = []

        static_img_dir = Path(settings.BASE_DIR) / "static" / "img"
        available_avatar_files = list(static_img_dir.glob("avatar*.jpg"))

        # Если нет доступных аватаров, используем дефолтный
        if not available_avatar_files:
            default_avatar = static_img_dir / "avatar.jpg"
            if default_avatar.exists():
                available_avatar_files = [default_avatar]

        # ЗАРАНЕЕ СОЗДАЕМ ВСЕ AVATARFILE ОБЪЕКТЫ
        # Это обеспечивает дедупликацию и правильное сохранение файлов
        ensure_avatar_directory_exists()  # Убеждаемся, что директория существует

        avatar_files_list = []  # Список созданных AvatarFile объектов

        if available_avatar_files:
            for avatar_file_path in tqdm(
                available_avatar_files, desc="Создание AvatarFile", unit="файл"
            ):
                # Читаем файл в память
                with open(avatar_file_path, "rb") as f:
                    file_content = f.read()

                # Создаем SimpleUploadedFile из содержимого файла
                file_obj = SimpleUploadedFile(
                    name=avatar_file_path.name,
                    content=file_content,
                    content_type="image/jpeg",
                )

                # Создаем или получаем существующий AvatarFile
                avatar_file = get_or_create_avatar_file(file_obj)
                avatar_files_list.append(avatar_file)

        # Размер пакета для bulk_create
        batch_size = 500
        # Хешируем пароль один раз для всех пользователей
        from django.contrib.auth.hashers import make_password

        hashed_password = make_password("12345")

        # Создаем пользователей пакетами
        for batch_start in tqdm(
            range(0, ratio, batch_size), desc="Создание пользователей", unit="пакет"
        ):
            batch_end = min(batch_start + batch_size, ratio)
            users_to_create = []
            profiles_to_create = []

            with transaction.atomic():
                # Создаем пользователей для текущего пакета
                for i in range(batch_start, batch_end):
                    username = fake.user_name() + str(i)  # Уникальный username
                    email = fake.email()
                    user = User(
                        username=username,
                        email=email,
                        password=hashed_password,  # Используем предварительно хешированный пароль
                        is_active=True,
                    )
                    users_to_create.append(user)

                # Создаем пользователей одним запросом
                created_users = User.objects.bulk_create(users_to_create)

                # Создаем профили для созданных пользователей
                for user in created_users:
                    profile = Profile(user=user, rating=0)
                    profiles_to_create.append(profile)

                # Создаем профили одним запросом
                Profile.objects.bulk_create(profiles_to_create)

                # Присваиваем аватары пользователям
                if avatar_files_list:
                    # Загружаем профили из БД после bulk_create, чтобы получить связи
                    user_ids = [user.id for user in created_users]
                    profiles = Profile.objects.filter(user_id__in=user_ids).select_related("user")
                    # Создаем словарь для быстрого доступа
                    profile_dict = {profile.user_id: profile for profile in profiles}

                    profiles_to_update = []
                    for user in created_users:
                        user_profile = profile_dict.get(user.id)
                        if user_profile is not None:
                            avatar_file = random.choice(avatar_files_list)
                            user_profile.avatar = avatar_file
                            profiles_to_update.append(user_profile)

                    Profile.objects.bulk_update(profiles_to_update, ["avatar"])

                users_list.extend(created_users)

        # Создаем вопросы
        questions_count = ratio * 10
        questions_to_create = []

        for _i in tqdm(range(questions_count), desc="Генерация вопросов", unit="вопрос"):
            # Случайный автор
            author = random.choice(users_list)

            # Генерируем вопрос
            question = Question(
                title=fake.sentence(nb_words=8).rstrip(".") + "?",
                text=fake.text(max_nb_chars=500),
                author=author,
                created_at=timezone.now()
                - timedelta(days=random.randint(0, 365)),  # Случайная дата за последний год
            )
            questions_to_create.append(question)

        # Создаем вопросы одним запросом
        questions_list = Question.objects.bulk_create(questions_to_create)

        # Добавляем теги к вопросам пакетно через through модель
        question_tag_relations = []
        for question in tqdm(questions_list, desc="Добавление тегов к вопросам", unit="вопрос"):
            num_tags = random.randint(1, 3)
            selected_tags = random.sample(tags_list, min(num_tags, len(tags_list)))
            for tag in selected_tags:
                question_tag_relations.append(
                    Question.tags.through(question_id=question.id, tag_id=tag.id)
                )

        # Создаем связи пакетно
        if question_tag_relations:
            Question.tags.through.objects.bulk_create(question_tag_relations, ignore_conflicts=True)

        # Создаем ответы
        answers_count = ratio * 100
        answers_to_create = []

        for _i in tqdm(range(answers_count), desc="Генерация ответов", unit="ответ"):
            # Случайный вопрос и автор
            question = random.choice(questions_list)
            author = random.choice(users_list)

            # Генерируем ответ
            answer = Answer(
                text=fake.text(max_nb_chars=300),
                author=author,
                question=question,
                created_at=question.created_at
                + timedelta(
                    days=random.randint(0, 30)
                ),  # Ответ создан в течение месяца после вопроса
                is_correct=random.choice([True, False]) if random.random() < 0.1 else False,
                # 10% ответов правильные
            )
            answers_to_create.append(answer)

        # Создаем ответы одним запросом
        Answer.objects.bulk_create(answers_to_create)

        # Создаем лайки на вопросы
        question_likes_count = ratio * 100
        question_likes_to_create: list[QuestionLike] = []
        question_likes_set = set()

        with tqdm(
            total=question_likes_count, desc="Генерация лайков на вопросы", unit="лайк"
        ) as pbar:
            attempts = 0
            max_attempts = question_likes_count * 10
            while len(question_likes_to_create) < question_likes_count and attempts < max_attempts:
                attempts += 1
                user = random.choice(users_list)
                question = random.choice(questions_list)
                value = random.choice([1, -1])  # Лайк или дизлайк

                # Проверяем уникальность (user, question)
                like_key = (user, question)
                if like_key not in question_likes_set:
                    question_likes_set.add(like_key)
                    question_likes_to_create.append(
                        QuestionLike(user=user, question=question, value=value)
                    )
                    pbar.update(1)

        # Создаем лайки одним запросом
        QuestionLike.objects.bulk_create(question_likes_to_create)

        question_ratings = QuestionLike.objects.values("question_id").annotate(total=Sum("value"))

        ratings_dict = {item["question_id"]: item["total"] for item in question_ratings}

        questions = Question.objects.all()
        questions_to_update = []

        for question in questions:
            new_rating = ratings_dict.get(question.id, 0)
            if question.rating != new_rating:
                question.rating = new_rating
                questions_to_update.append(question)

        if questions_to_update:
            Question.objects.bulk_update(questions_to_update, ["rating"])

        # Создаем лайки на ответы
        answer_likes_count = ratio * 100
        answers = list(Answer.objects.all())
        answer_likes_to_create: list[AnswerLike] = []
        answer_likes_set = set()

        with tqdm(total=answer_likes_count, desc="Генерация лайков на ответы", unit="лайк") as pbar:
            attempts = 0
            max_attempts = answer_likes_count * 10
            while len(answer_likes_to_create) < answer_likes_count and attempts < max_attempts:
                attempts += 1
                user = random.choice(users_list)
                answer = random.choice(answers)
                value = random.choice([1, -1])  # Лайк или дизлайк

                # Проверяем уникальность (user, answer)
                like_key = (user, answer)
                if like_key not in answer_likes_set:
                    answer_likes_set.add(like_key)
                    answer_likes_to_create.append(AnswerLike(user=user, answer=answer, value=value))
                    pbar.update(1)

        answer_ratings = AnswerLike.objects.values("answer_id").annotate(total=Sum("value"))

        ratings_dict = {item["answer_id"]: item["total"] for item in answer_ratings}

        answers = Answer.objects.all()
        answers_to_update = []

        for answer in answers:
            new_rating = ratings_dict.get(answer.id, 0)
            if answer.rating != new_rating:
                answer.rating = new_rating
                answers_to_update.append(answer)

        if answers_to_update:
            Answer.objects.bulk_update(answers_to_update, ["rating"])

        question_ratings = (
            QuestionLike.objects.select_related("question")
            .values("question__author_id")
            .annotate(total=Sum("value"))
        )
        q_ratings_dict = {item["question__author_id"]: item["total"] for item in question_ratings}

        answer_ratings = (
            AnswerLike.objects.select_related("answer")
            .values("answer__author_id")
            .annotate(total=Sum("value"))
        )
        a_ratings_dict = {item["answer__author_id"]: item["total"] for item in answer_ratings}

        profiles = Profile.objects.all()
        profiles_to_update = []

        for profile in profiles:
            user_id = profile.user_id
            q_rating = q_ratings_dict.get(user_id, 0)
            a_rating = a_ratings_dict.get(user_id, 0)
            new_rating = q_rating + a_rating

            if profile.rating != new_rating:
                profile.rating = new_rating
                profiles_to_update.append(profile)

        if profiles_to_update:
            Profile.objects.bulk_update(profiles_to_update, ["rating"])

        # Вычисляем время выполнения
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60

        # Статистика
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("База данных успешно заполнена!"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"Теги: {Tag.objects.count()}")
        self.stdout.write(f"Пользователи: {User.objects.count()}")
        self.stdout.write(f"Вопросы: {Question.objects.count()}")
        self.stdout.write(f"Ответы: {Answer.objects.count()}")
        self.stdout.write(f"Лайки на вопросы: {QuestionLike.objects.count()}")
        self.stdout.write(f"Лайки на ответы: {AnswerLike.objects.count()}")
        if minutes > 0:
            self.stdout.write(f"Время выполнения: {minutes} мин {seconds:.2f} сек")
        else:
            self.stdout.write(f"Время выполнения: {seconds:.2f} сек")
        self.stdout.write("=" * 50)
