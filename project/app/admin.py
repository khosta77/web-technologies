"""
Админ-панель Django для приложения AskPupkin
"""

from django.contrib import admin

from .models import Answer, AnswerLike, Profile, Question, QuestionLike, Tag


# Inline классы
class AnswerInline(admin.TabularInline):
    """Inline для отображения ответов в QuestionAdmin"""

    model = Answer
    extra = 0
    fields = ["text", "author", "rating", "is_correct", "created_at"]
    raw_id_fields = ["author"]
    readonly_fields = ["rating", "created_at"]
    show_change_link = True


class QuestionLikeInline(admin.TabularInline):
    """Inline для отображения лайков в QuestionAdmin"""

    model = QuestionLike
    extra = 0
    fields = ["user", "value"]
    raw_id_fields = ["user"]
    show_change_link = True


class AnswerLikeInline(admin.TabularInline):
    """Inline для отображения лайков в AnswerAdmin"""

    model = AnswerLike
    extra = 0
    fields = ["user", "value"]
    raw_id_fields = ["user"]
    show_change_link = True


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Админ-панель для профилей пользователей"""

    list_display = ["user", "avatar", "get_rating", "get_questions_count", "get_answers_count"]
    list_filter = ["rating"]
    search_fields = ["user__username", "user__email"]
    raw_id_fields = ["user"]
    list_select_related = ["user"]
    list_per_page = 25

    fieldsets = (
        ("Основная информация", {"fields": ("user", "avatar")}),
        ("Рейтинг", {"fields": ("rating",), "classes": ("collapse",)}),
    )

    readonly_fields = ["rating"]

    def get_rating(self, obj: Profile) -> int:
        """Получить рейтинг пользователя"""
        return obj.get_rating()

    get_rating.short_description = "Рейтинг"  # type: ignore[attr-defined]

    def get_questions_count(self, obj: Profile) -> int:
        """Получить количество вопросов пользователя"""
        count: int = obj.user.questions.count()
        return count

    get_questions_count.short_description = "Вопросов"  # type: ignore[attr-defined]

    def get_answers_count(self, obj: Profile) -> int:
        """Получить количество ответов пользователя"""
        count: int = obj.user.answers.count()
        return count

    get_answers_count.short_description = "Ответов"  # type: ignore[attr-defined]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-панель для тегов"""

    list_display = ["name", "get_questions_count"]
    search_fields = ["name"]
    list_per_page = 25

    def get_questions_count(self, obj: Tag) -> int:
        """Получить количество вопросов с этим тегом"""
        count: int = obj.questions.count()
        return count

    get_questions_count.short_description = "Количество вопросов"  # type: ignore[attr-defined]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Админ-панель для вопросов"""

    list_display = ["title", "author", "rating", "created_at", "get_answers_count"]
    list_filter = ["created_at", "rating", "tags", "author"]
    search_fields = ["title", "text", "author__username", "id"]
    filter_horizontal = ["tags"]
    raw_id_fields = ["author"]
    readonly_fields = ["rating", "created_at"]
    list_select_related = ["author", "author__profile"]
    list_prefetch_related = ["tags", "answers"]
    date_hierarchy = "created_at"
    list_per_page = 25
    inlines = [AnswerInline, QuestionLikeInline]

    fieldsets = (
        ("Основная информация", {"fields": ("title", "text", "author", "tags")}),
        ("Метаданные", {"fields": ("rating", "created_at"), "classes": ("collapse",)}),
    )

    def get_answers_count(self, obj: Question) -> int:
        """Получить количество ответов"""
        if hasattr(obj, "_prefetched_objects_cache") and "answers" in obj._prefetched_objects_cache:
            return len(obj._prefetched_objects_cache["answers"])
        return obj.get_answers_count()

    get_answers_count.short_description = "Количество ответов"  # type: ignore[attr-defined]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Админ-панель для ответов"""

    list_display = ["question", "author", "rating", "is_correct", "created_at"]
    list_filter = ["is_correct", "created_at", "rating", "author", "question"]
    search_fields = ["text", "question__title", "author__username", "id"]
    raw_id_fields = ["author", "question"]
    readonly_fields = ["rating", "created_at"]
    list_select_related = ["author", "author__profile", "question"]
    date_hierarchy = "created_at"
    list_per_page = 25
    inlines = [AnswerLikeInline]

    fieldsets = (
        ("Основная информация", {"fields": ("question", "text", "author", "is_correct")}),
        ("Метаданные", {"fields": ("rating", "created_at"), "classes": ("collapse",)}),
    )


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    """Админ-панель для лайков вопросов"""

    list_display = ["user", "question", "value", "question__rating"]
    list_filter = ["value", "question"]
    search_fields = ["user__username", "question__title", "id"]
    raw_id_fields = ["user", "question"]
    list_select_related = ["user", "user__profile", "question"]
    list_per_page = 25

    fieldsets = (("Основная информация", {"fields": ("user", "question", "value")}),)

    def question__rating(self, obj: QuestionLike) -> int:
        """Получить рейтинг вопроса"""
        rating: int = obj.question.rating
        return rating

    question__rating.short_description = "Рейтинг вопроса"  # type: ignore[attr-defined]


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    """Админ-панель для лайков ответов"""

    list_display = ["user", "answer", "value", "answer__rating"]
    list_filter = ["value", "answer"]
    search_fields = ["user__username", "answer__text", "id"]
    raw_id_fields = ["user", "answer"]
    list_select_related = ["user", "user__profile", "answer", "answer__question", "answer__author"]
    list_per_page = 25

    fieldsets = (("Основная информация", {"fields": ("user", "answer", "value")}),)

    def answer__rating(self, obj: AnswerLike) -> int:
        """Получить рейтинг ответа"""
        rating: int = obj.answer.rating
        return rating

    answer__rating.short_description = "Рейтинг ответа"  # type: ignore[attr-defined]
