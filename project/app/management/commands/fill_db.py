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

import random

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

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
        self.stdout.write(f"[ ] Создание {ratio} тегов...")
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

        for i in range(ratio):
            if i < len(popular_tags):
                tag_name = popular_tags[i]
            else:
                # Генерируем уникальный тег
                tag_name = fake.word().lower()
                while tag_name in tag_names or len(tag_name) > 50:
                    tag_name = fake.word().lower()
                tag_name = tag_name.replace(" ", "-")

            tag_names.add(tag_name)
            tag = Tag.objects.create(name=tag_name)
            tags_list.append(tag)

        self.stdout.write(self.style.SUCCESS(f"[X] Создано {len(tags_list)} тегов"))

        # Создаем пользователей
        self.stdout.write(f"[ ] Создание {ratio} пользователей...")
        users_list = []
        for i in range(ratio):
            username = fake.user_name() + str(i)  # Уникальный username
            email = fake.email()
            user = User.objects.create_user(
                username=username,
                email=email,
                password="12345",  # Простой пароль для тестирования
            )
            # Profile создается автоматически через сигналы
            # Проверяем, что профиль создан, если нет - создаем вручную
            if not hasattr(user, "profile"):
                Profile.objects.create(
                    user=user,
                    avatar="img/avatar.jpg",  # Дефолтный аватар
                )
            users_list.append(user)

        self.stdout.write(self.style.SUCCESS(f"[X] Создано {len(users_list)} пользователей"))

        # Создаем вопросы
        questions_count = ratio * 10
        self.stdout.write(f"[ ] Создание {questions_count} вопросов...")
        questions_list = []

        for _i in range(questions_count):
            # Случайный автор
            author = random.choice(users_list)

            # Генерируем вопрос
            question = Question.objects.create(
                title=fake.sentence(nb_words=8).rstrip(".") + "?",
                text=fake.text(max_nb_chars=500),
                author=author,
                created_at=timezone.now()
                - timedelta(days=random.randint(0, 365)),  # Случайная дата за последний год
            )

            # Добавляем случайные теги (от 1 до 3)
            num_tags = random.randint(1, 3)
            question.tags.add(*random.sample(tags_list, min(num_tags, len(tags_list))))
            questions_list.append(question)

        self.stdout.write(self.style.SUCCESS(f"[X] Создано {len(questions_list)} вопросов"))

        # Создаем ответы
        answers_count = ratio * 100
        self.stdout.write(f"[ ] Создание {answers_count} ответов...")

        for _i in range(answers_count):
            # Случайный вопрос и автор
            question = random.choice(questions_list)
            author = random.choice(users_list)

            # Генерируем ответ
            answer = Answer.objects.create(
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

        self.stdout.write(self.style.SUCCESS(f"[X] Создано {answers_count} ответов"))

        # Создаем лайки на вопросы
        question_likes_count = ratio * 100  # Половина от общего количества лайков
        self.stdout.write(f"[ ] Создание {question_likes_count} лайков на вопросы...")

        created_likes = 0
        attempts = 0
        max_attempts = question_likes_count * 10

        while created_likes < question_likes_count and attempts < max_attempts:
            attempts += 1
            user = random.choice(users_list)
            question = random.choice(questions_list)
            value = random.choice([1, -1])  # Лайк или дизлайк

            # Проверяем, что пользователь еще не ставил лайк этому вопросу
            _like, created = QuestionLike.objects.get_or_create(
                user=user,
                question=question,
                defaults={"value": value},
            )
            if created:
                created_likes += 1

        # Обновляем рейтинги вопросов
        for question in questions_list:
            question.update_rating()

        self.stdout.write(self.style.SUCCESS(f"[X] Создано {created_likes} лайков на вопросы"))

        # Создаем лайки на ответы
        answer_likes_count = ratio * 100  # Вторая половина лайков
        self.stdout.write(f"[ ] Создание {answer_likes_count} лайков на ответы...")

        answers = list(Answer.objects.all())
        created_likes = 0
        attempts = 0
        max_attempts = answer_likes_count * 10

        while created_likes < answer_likes_count and attempts < max_attempts:
            attempts += 1
            user = random.choice(users_list)
            answer = random.choice(answers)
            value = random.choice([1, -1])  # Лайк или дизлайк

            # Проверяем, что пользователь еще не ставил лайк этому ответу
            _like, created = AnswerLike.objects.get_or_create(
                user=user,
                answer=answer,
                defaults={"value": value},
            )
            if created:
                created_likes += 1

        # Обновляем рейтинги ответов
        for answer in Answer.objects.all():
            answer.update_rating()

        self.stdout.write(self.style.SUCCESS(f"[X] Создано {created_likes} лайков на ответы"))

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
        self.stdout.write("=" * 50)
