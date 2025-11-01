"""
Модели Django для приложения AskPupkin
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Profile(models.Model):
    """Профиль пользователя - расширение стандартной модели User"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        default="img/avatar.jpg",
        verbose_name="Аватар",
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"

    def get_rating(self) -> int:
        """Получить рейтинг пользователя (сумма лайков на вопросы и ответы)"""
        # Используем строковые ссылки для избежания циклических импортов
        from django.db.models import Sum

        question_likes = (
            QuestionLike.objects.filter(question__author=self.user).aggregate(total=Sum("value"))[
                "total"
            ]
            or 0
        )
        answer_likes = (
            AnswerLike.objects.filter(answer__author=self.user).aggregate(total=Sum("value"))[
                "total"
            ]
            or 0
        )
        return question_likes + answer_likes


class Tag(models.Model):
    """Тег для вопросов"""

    name = models.CharField(max_length=50, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self) -> str:
        return str(self.name)


class QuestionManager(models.Manager):
    """Кастомный менеджер для вопросов"""

    def new(self) -> models.QuerySet[Question]:
        """Новые вопросы (по дате создания, новые сначала)"""
        return self.get_queryset().order_by("-created_at")

    def hot(self) -> models.QuerySet[Question]:
        """Популярные вопросы (по рейтингу, по убыванию)"""
        return self.get_queryset().order_by("-rating", "-created_at")

    def by_tag(self, tag_name: str) -> models.QuerySet[Question]:
        """Вопросы по тегу"""
        return self.get_queryset().filter(tags__name=tag_name).distinct()


class Question(models.Model):
    """Вопрос"""

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст вопроса")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
    )
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")
    tags = models.ManyToManyField(Tag, related_name="questions", verbose_name="Теги")

    objects = QuestionManager()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.title)

    def get_absolute_url(self) -> str:
        """Получить абсолютный URL для вопроса"""
        return str(reverse("question", kwargs={"question_id": self.id}))

    def get_answers_count(self) -> int:
        """Получить количество ответов на вопрос"""
        count: int = self.answers.count()
        return count

    def update_rating(self) -> None:
        """Обновить рейтинг вопроса на основе лайков"""
        total = (
            QuestionLike.objects.filter(question=self).aggregate(total=models.Sum("value"))["total"]
            or 0
        )
        self.rating = total
        self.save(update_fields=["rating"])


class Answer(models.Model):
    """Ответ на вопрос"""

    text = models.TextField(verbose_name="Текст ответа")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Автор",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="Правильный ответ",
    )
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        ordering = ["-rating", "-created_at"]

    def __str__(self) -> str:
        return f"Answer to {self.question.title[:50]}"

    def update_rating(self) -> None:
        """Обновить рейтинг ответа на основе лайков"""
        total = (
            AnswerLike.objects.filter(answer=self).aggregate(total=models.Sum("value"))["total"]
            or 0
        )
        self.rating = total
        self.save(update_fields=["rating"])


class QuestionLike(models.Model):
    """Лайк (оценка) вопроса"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="question_likes",
        verbose_name="Пользователь",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Вопрос",
    )
    value = models.IntegerField(
        default=0,
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
        verbose_name="Значение",
        help_text="+1 для лайка, -1 для дизлайка",
    )

    class Meta:
        verbose_name = "Оценка вопроса"
        verbose_name_plural = "Оценки вопросов"
        unique_together = [["user", "question"]]

    def __str__(self) -> str:
        return f"{self.user.username} -> {self.question.title[:50]} ({self.value})"

    def save(self, *args: object, **kwargs: object) -> None:
        """Переопределяем save для обновления рейтинга вопроса"""
        super().save(*args, **kwargs)
        self.question.update_rating()

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict[str, int]]:
        """Переопределяем delete для обновления рейтинга вопроса"""
        result: tuple[int, dict[str, int]] = super().delete(*args, **kwargs)
        self.question.update_rating()
        return result


class AnswerLike(models.Model):
    """Лайк (оценка) ответа"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answer_likes",
        verbose_name="Пользователь",
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Ответ",
    )
    value = models.IntegerField(
        default=0,
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
        verbose_name="Значение",
        help_text="+1 для лайка, -1 для дизлайка",
    )

    class Meta:
        verbose_name = "Оценка ответа"
        verbose_name_plural = "Оценки ответов"
        unique_together = [["user", "answer"]]

    def __str__(self) -> str:
        return f"{self.user.username} -> Answer {self.answer.id} ({self.value})"

    def save(self, *args: object, **kwargs: object) -> None:
        """Переопределяем save для обновления рейтинга ответа"""
        super().save(*args, **kwargs)
        self.answer.update_rating()

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict[str, int]]:
        """Переопределяем delete для обновления рейтинга ответа"""
        result: tuple[int, dict[str, int]] = super().delete(*args, **kwargs)
        self.answer.update_rating()
        return result
