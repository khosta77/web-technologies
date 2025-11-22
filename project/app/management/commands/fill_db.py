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
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone
from faker import Faker
from tqdm import tqdm

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

                # Обновляем аватары для всех пользователей
                if available_avatar_files:
                    # Загружаем профили из БД после bulk_create, чтобы получить связи
                    user_ids = [user.id for user in created_users]
                    profiles = Profile.objects.filter(user_id__in=user_ids).select_related("user")
                    # Создаем словарь для быстрого доступа
                    profile_dict = {profile.user_id: profile for profile in profiles}

                    for user in tqdm(
                        created_users, desc="Сохранение аватаров", unit="аватар", leave=False
                    ):
                        profile = profile_dict.get(user.id)
                        if profile:
                            avatar_file_path = random.choice(available_avatar_files)
                            with open(avatar_file_path, "rb") as f:
                                profile.avatar.save(avatar_file_path.name, File(f), save=False)
                            profile.save(update_fields=["avatar"])

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

        # Обновляем рейтинги вопросов через JOIN (оптимизировано для PostgreSQL)
        self.stdout.write("Обновление рейтингов вопросов через SQL")
        with connection.cursor() as cursor:
            # Обновляем вопросы с лайками через JOIN
            cursor.execute(
                """
                UPDATE app_question q
                SET rating = COALESCE(agg.total, 0)
                FROM (
                    SELECT question_id, SUM(value) as total
                    FROM app_questionlike
                    GROUP BY question_id
                ) agg
                WHERE q.id = agg.question_id
                """
            )
            # Обновляем вопросы без лайков (устанавливаем 0)
            cursor.execute(
                """
                UPDATE app_question
                SET rating = 0
                WHERE id NOT IN (SELECT DISTINCT question_id FROM app_questionlike WHERE question_id IS NOT NULL)
                """
            )

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

        # Обновляем рейтинги ответов через JOIN (оптимизировано для PostgreSQL)
        self.stdout.write("Обновление рейтингов ответов через SQL")
        with connection.cursor() as cursor:
            # Обновляем ответы с лайками через JOIN
            cursor.execute(
                """
                UPDATE app_answer a
                SET rating = COALESCE(agg.total, 0)
                FROM (
                    SELECT answer_id, SUM(value) as total
                    FROM app_answerlike
                    GROUP BY answer_id
                ) agg
                WHERE a.id = agg.answer_id
                """
            )
            # Обновляем ответы без лайков (устанавливаем 0)
            cursor.execute(
                """
                UPDATE app_answer
                SET rating = 0
                WHERE id NOT IN (SELECT DISTINCT answer_id FROM app_answerlike WHERE answer_id IS NOT NULL)
                """
            )

        # Обновляем рейтинги профилей пользователей через JOIN (оптимизировано для PostgreSQL)
        self.stdout.write("Обновление рейтингов профилей пользователей через SQL")
        with connection.cursor() as cursor:
            # Обновляем профили с лайками через LEFT JOIN (объединяем рейтинги вопросов и ответов)
            cursor.execute(
                """
                UPDATE app_profile p
                SET rating = COALESCE(q_rating.total, 0) + COALESCE(a_rating.total, 0)
                FROM (
                    SELECT q.author_id, SUM(ql.value) as total
                    FROM app_questionlike ql
                    JOIN app_question q ON ql.question_id = q.id
                    GROUP BY q.author_id
                ) q_rating
                LEFT JOIN (
                    SELECT a.author_id, SUM(al.value) as total
                    FROM app_answerlike al
                    JOIN app_answer a ON al.answer_id = a.id
                    GROUP BY a.author_id
                ) a_rating ON q_rating.author_id = a_rating.author_id
                WHERE p.user_id = q_rating.author_id
                """
            )
            # Обновляем профили, у которых есть только лайки на ответы (но нет на вопросы)
            cursor.execute(
                """
                UPDATE app_profile p
                SET rating = COALESCE(a_rating.total, 0)
                FROM (
                    SELECT a.author_id, SUM(al.value) as total
                    FROM app_answerlike al
                    JOIN app_answer a ON al.answer_id = a.id
                    GROUP BY a.author_id
                ) a_rating
                WHERE p.user_id = a_rating.author_id
                AND p.user_id NOT IN (
                    SELECT DISTINCT q.author_id FROM app_question q
                    JOIN app_questionlike ql ON q.id = ql.question_id
                )
                """
            )
            # Обновляем профили без лайков (устанавливаем 0)
            cursor.execute(
                """
                UPDATE app_profile
                SET rating = 0
                WHERE user_id NOT IN (
                    SELECT DISTINCT q.author_id FROM app_question q
                    JOIN app_questionlike ql ON q.id = ql.question_id
                    UNION
                    SELECT DISTINCT a.author_id FROM app_answer a
                    JOIN app_answerlike al ON a.id = al.answer_id
                )
                """
            )

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
