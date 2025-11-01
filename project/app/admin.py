"""
Админ-панель Django для приложения AskPupkin
"""

from django.contrib import admin

from .models import Answer, AnswerLike, Profile, Question, QuestionLike, Tag


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Админ-панель для профилей пользователей"""

    list_display = ["user", "avatar", "get_rating"]
    list_filter = ["user"]
    search_fields = ["user__username", "user__email"]

    def get_rating(self, obj: Profile) -> int:
        """Получить рейтинг пользователя"""
        return obj.get_rating()

    get_rating.short_description = "Рейтинг"  # type: ignore[attr-defined]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-панель для тегов"""

    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Админ-панель для вопросов"""

    list_display = ["title", "author", "rating", "created_at", "get_answers_count"]
    list_filter = ["created_at", "rating", "tags"]
    search_fields = ["title", "text", "author__username"]
    filter_horizontal = ["tags"]
    readonly_fields = ["rating", "created_at"]

    def get_answers_count(self, obj: Question) -> int:
        """Получить количество ответов"""
        return obj.get_answers_count()

    get_answers_count.short_description = "Количество ответов"  # type: ignore[attr-defined]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Админ-панель для ответов"""

    list_display = ["question", "author", "rating", "is_correct", "created_at"]
    list_filter = ["is_correct", "created_at", "rating"]
    search_fields = ["text", "question__title", "author__username"]
    readonly_fields = ["rating", "created_at"]


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    """Админ-панель для лайков вопросов"""

    list_display = ["user", "question", "value", "question__rating"]
    list_filter = ["value"]
    search_fields = ["user__username", "question__title"]

    def question__rating(self, obj: QuestionLike) -> int:
        """Получить рейтинг вопроса"""
        rating: int = obj.question.rating
        return rating

    question__rating.short_description = "Рейтинг вопроса"  # type: ignore[attr-defined]


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    """Админ-панель для лайков ответов"""

    list_display = ["user", "answer", "value", "answer__rating"]
    list_filter = ["value"]
    search_fields = ["user__username", "answer__text"]

    def answer__rating(self, obj: AnswerLike) -> int:
        """Получить рейтинг ответа"""
        rating: int = obj.answer.rating
        return rating

    answer__rating.short_description = "Рейтинг ответа"  # type: ignore[attr-defined]
