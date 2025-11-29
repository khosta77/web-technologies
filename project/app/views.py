"""
Views для приложения AskPupkin
"""

from __future__ import annotations

import contextlib
import traceback

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from .avatar_utils import get_default_avatar_file, get_or_create_avatar_file
from .constants import ANSWERS_PER_PAGE, QUESTIONS_PER_PAGE
from .forms import AddAnswerForm, AskQuestionForm, EditProfileForm, LoginForm, SignupForm
from .models import Answer, AnswerLike, Profile, Question, QuestionLike, Tag
from .repositories import (
    AnswerRepository,
    QuestionRepository,
    TagRepository,
    UserRepository,
)
from .utils import paginate


# Создаем экземпляры репозиториев
question_repository = QuestionRepository()
answer_repository = AnswerRepository()
tag_repository = TagRepository()
user_repository = UserRepository()


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница - список новых вопросов"""
    questions = question_repository.get_all_questions()
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)

    # Получаем информацию о лайках пользователя для вопросов на странице
    user_question_likes = {}
    if request.user.is_authenticated:
        question_ids = [q.id for q in page]
        if question_ids:
            question_likes = QuestionLike.objects.filter(
                user=request.user, question_id__in=question_ids
            ).select_related("question")
            for like in question_likes:
                user_question_likes[like.question.id] = like.value

    return render(request, "index.html", {"page": page, "user_question_likes": user_question_likes})


def hot(request: HttpRequest) -> HttpResponse:
    """Список популярных вопросов"""
    questions = question_repository.get_hot_questions()
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)

    # Получаем информацию о лайках пользователя для вопросов на странице
    user_question_likes = {}
    if request.user.is_authenticated:
        question_ids = [q.id for q in page]
        if question_ids:
            question_likes = QuestionLike.objects.filter(
                user=request.user, question_id__in=question_ids
            ).select_related("question")
            for like in question_likes:
                user_question_likes[like.question.id] = like.value

    return render(
        request,
        "index.html",
        {"page": page, "is_hot": True, "user_question_likes": user_question_likes},
    )


def question(request: HttpRequest, question_id: int) -> HttpResponse:
    """Страница одного вопроса"""
    question_obj = question_repository.get_question_by_id(question_id)
    if question_obj is None:
        raise Http404("Question not found")

    # Обработка формы добавления ответа
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"/login/?next={question_obj.get_absolute_url()}")

        form = AddAnswerForm(request.POST)
        if form.is_valid():
            answer = Answer.objects.create(
                text=form.cleaned_data["text"],
                author=request.user,
                question=question_obj,
            )
            messages.success(request, "Ответ успешно добавлен")
            # Редирект на страницу вопроса с якорем на добавленный ответ
            return redirect(f"{question_obj.get_absolute_url()}#answer-{answer.id}")
        else:
            messages.error(request, "Ошибка при добавлении ответа. Проверьте введенные данные.")
    else:
        form = AddAnswerForm()

    answers = answer_repository.get_answers_by_question_id(question_id)
    page = paginate(answers, request, per_page=ANSWERS_PER_PAGE)

    # Получаем информацию о лайках пользователя (если авторизован)
    user_question_like = None
    user_answer_likes = {}
    if request.user.is_authenticated:
        with contextlib.suppress(QuestionLike.DoesNotExist):
            user_question_like = QuestionLike.objects.get(user=request.user, question=question_obj)

        # Получаем лайки для всех ответов на странице
        answer_ids = [answer.id for answer in page]
        if answer_ids:
            answer_likes = AnswerLike.objects.filter(
                user=request.user, answer_id__in=answer_ids
            ).select_related("answer")
            for like in answer_likes:
                user_answer_likes[like.answer.id] = like.value

    return render(
        request,
        "question.html",
        {
            "question": question_obj,
            "page": page,
            "form": form,
            "user_question_like": user_question_like,
            "user_answer_likes": user_answer_likes,
        },
    )


def tag(request: HttpRequest, tag_name: str) -> HttpResponse:
    """Список вопросов по тегу"""
    questions = question_repository.get_questions_by_tag(tag_name)
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)

    # Получаем информацию о лайках пользователя для вопросов на странице
    user_question_likes = {}
    if request.user.is_authenticated:
        question_ids = [q.id for q in page]
        if question_ids:
            question_likes = QuestionLike.objects.filter(
                user=request.user, question_id__in=question_ids
            ).select_related("question")
            for like in question_likes:
                user_question_likes[like.question.id] = like.value

    return render(
        request,
        "index.html",
        {"page": page, "tag_name": tag_name, "user_question_likes": user_question_likes},
    )


def tags(request: HttpRequest) -> HttpResponse:
    """Страница списка тегов"""
    tags_list = tag_repository.get_all_tags()
    return render(request, "tags.html", {"tags_list": tags_list})


def login_view(request: HttpRequest) -> HttpResponse:
    """Форма авторизации"""
    # Если пользователь уже авторизован, редиректим на главную
    if request.user.is_authenticated:
        return redirect("index")

    # Получаем параметр next из GET-запроса
    next_url = request.GET.get("next", "/")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)  # AuthenticationForm требует request
        if form.is_valid():
            login(request, form.get_user())  # Используем встроенный метод
            # Получаем next из POST (если был передан) или из GET, иначе "/"
            next_url = request.POST.get("next", request.GET.get("next", "/"))

            # ВАЖНО: Проверяем безопасность URL перед редиректом
            # Защита от Open Redirect уязвимости
            if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                next_url = "/"

            return redirect(next_url)
    else:
        form = LoginForm(request)

    # Также проверяем next_url для шаблона
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = "/"

    return render(request, "login.html", {"form": form, "next": next_url})


def signup(request: HttpRequest) -> HttpResponse:
    """Форма регистрации"""
    # Если пользователь уже авторизован, редиректим на главную
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            # UserCreationForm уже создает пользователя, но нам нужно сохранить email
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()
            # Создаем профиль
            profile = Profile.objects.create(user=user, rating=0)
            # Сохраняем аватар, если загружен, иначе используем аватар по умолчанию
            avatar = form.cleaned_data.get("avatar")
            if avatar:
                avatar_file = get_or_create_avatar_file(avatar)
                profile.avatar = avatar_file
                profile.save(update_fields=["avatar"])
            else:
                # Устанавливаем аватар по умолчанию из static/img/avatar.jpg
                default_avatar_file = get_default_avatar_file()
                if default_avatar_file:
                    profile.avatar = default_avatar_file
                    profile.save(update_fields=["avatar"])
            # Автоматически логиним пользователя
            login(request, user)
            messages.success(
                request, f"Добро пожаловать, {user.username}! Регистрация прошла успешно."
            )
            return redirect("index")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


@login_required(login_url="/login/")
def ask(request: HttpRequest) -> HttpResponse:
    """Форма добавления вопроса"""
    if request.method == "POST":
        form = AskQuestionForm(request.POST)
        if form.is_valid():
            # Создаем вопрос
            question_obj = Question.objects.create(
                title=form.cleaned_data["title"],
                text=form.cleaned_data["text"],
                author=request.user,
            )
            # Обрабатываем теги
            tags_list = form.cleaned_data.get("tags", [])
            for tag_name in tags_list:
                # Получаем или создаем тег
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                question_obj.tags.add(tag_obj)
            messages.success(request, "Вопрос успешно добавлен")
            return redirect(question_obj.get_absolute_url())
    else:
        form = AskQuestionForm()

    return render(request, "ask.html", {"form": form})


@login_required(login_url="/login/")
def settings(request: HttpRequest) -> HttpResponse:
    """Страница настроек профиля"""
    if request.method == "POST":
        has_avatar_file = "avatar" in request.FILES

        form = EditProfileForm(
            request.POST, request.FILES, instance=request.user, user=request.user
        )

        if form.is_valid():
            # Сохраняем изменения username и email через форму
            user = form.save(commit=False)
            # Обновляем пароль, если указан
            new_password = form.cleaned_data.get("new_password")
            if new_password:
                user.set_password(new_password)
            user.save()

            # Обновляем аватар, если загружен
            # Проверяем как через cleaned_data, так и через request.FILES
            avatar = form.cleaned_data.get("avatar")
            if not avatar and has_avatar_file:
                # Если файл есть в request.FILES, но не в cleaned_data, берем из request.FILES
                avatar = request.FILES.get("avatar")

            if avatar:
                # Получаем или создаем профиль
                profile, _created = Profile.objects.get_or_create(user=user, defaults={"rating": 0})
                try:
                    avatar_file = get_or_create_avatar_file(avatar)
                    profile.avatar = avatar_file
                    profile.save(update_fields=["avatar"])
                except Exception as e:
                    error_msg = f"Ошибка при загрузке аватара: {e!s}"
                    messages.error(request, error_msg)
                    # Логируем полную ошибку для отладки
                    print(f"Avatar upload error: {traceback.format_exc()}")
            elif has_avatar_file:
                messages.warning(
                    request, "Файл был выбран, но не был обработан. Попробуйте еще раз."
                )
            else:
                messages.success(request, "Профиль успешно обновлён")
            return redirect("settings")
        else:
            # Если форма не валидна, показываем ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            # Также проверяем, есть ли файл в request.FILES, даже если форма не валидна
            if has_avatar_file:
                messages.warning(
                    request,
                    "Файл был выбран, но форма не прошла валидацию. "
                    "Проверьте другие поля и попробуйте снова.",
                )
    else:
        form = EditProfileForm(instance=request.user, user=request.user)

    questions = (
        Question.objects.filter(author=request.user)
        .select_related("author", "author__profile")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    answers = (
        Answer.objects.filter(author=request.user)
        .select_related("author", "author__profile", "question")
        .order_by("-created_at")
    )

    # Получаем информацию о лайках пользователя для вопросов и ответов
    user_question_likes = {}
    user_answer_likes = {}
    if request.user.is_authenticated:
        question_ids = [q.id for q in questions]
        if question_ids:
            question_likes = QuestionLike.objects.filter(
                user=request.user, question_id__in=question_ids
            ).select_related("question")
            for like in question_likes:
                user_question_likes[like.question.id] = like.value

        answer_ids = [a.id for a in answers]
        if answer_ids:
            answer_likes = AnswerLike.objects.filter(
                user=request.user, answer_id__in=answer_ids
            ).select_related("answer")
            for like in answer_likes:
                user_answer_likes[like.answer.id] = like.value

    return render(
        request,
        "settings.html",
        {
            "form": form,
            "user_questions": questions,
            "user_answers": answers,
            "user_question_likes": user_question_likes,
            "user_answer_likes": user_answer_likes,
        },
    )


def profile(request: HttpRequest, user_id: int) -> HttpResponse:
    """Страница профиля пользователя"""
    try:
        profile_user = User.objects.get(id=user_id)
    except User.DoesNotExist as e:
        raise Http404("User not found") from e

    user_questions = (
        Question.objects.filter(author=profile_user)
        .select_related("author", "author__profile")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    user_answers = (
        Answer.objects.filter(author=profile_user)
        .select_related("author", "author__profile", "question")
        .order_by("-created_at")
    )

    # Получаем информацию о лайках текущего пользователя для вопросов и ответов
    user_question_likes = {}
    user_answer_likes = {}
    if request.user.is_authenticated:
        question_ids = [q.id for q in user_questions]
        if question_ids:
            question_likes = QuestionLike.objects.filter(
                user=request.user, question_id__in=question_ids
            ).select_related("question")
            for like in question_likes:
                user_question_likes[like.question.id] = like.value

        answer_ids = [a.id for a in user_answers]
        if answer_ids:
            answer_likes = AnswerLike.objects.filter(
                user=request.user, answer_id__in=answer_ids
            ).select_related("answer")
            for like in answer_likes:
                user_answer_likes[like.answer.id] = like.value

    return render(
        request,
        "profile.html",
        {
            "profile_user": profile_user,
            "user_questions": user_questions,
            "user_answers": user_answers,
            "user_question_likes": user_question_likes,
            "user_answer_likes": user_answer_likes,
        },
    )


def logout_view(request: HttpRequest) -> HttpResponse:
    """Выход из системы"""
    if request.user.is_authenticated:
        from django.contrib.auth import logout

        logout(request)
        messages.success(request, "Вы успешно вышли из системы")
    # Редирект на текущую страницу или главную
    referer = request.META.get("HTTP_REFERER", "/")
    return redirect(referer if referer else "index")


def custom_404_view(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    """Кастомная страница 404"""
    return render(request, "404.html", {}, status=404)


@login_required(login_url="/login/")
@require_http_methods(["POST"])
def like_question(request: HttpRequest) -> JsonResponse:
    """AJAX обработчик для лайка/дизлайка вопроса"""
    try:
        question_id = int(request.POST.get("question_id", 0))
        value = int(request.POST.get("value", 0))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Неверные параметры запроса"}, status=400)

    if value not in [-1, 1]:
        return JsonResponse({"error": "Значение должно быть -1 или 1"}, status=400)

    try:
        question_obj = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return JsonResponse({"error": "Вопрос не найден"}, status=404)

    # Получаем или создаем лайк
    like, created = QuestionLike.objects.get_or_create(
        user=request.user,
        question=question_obj,
        defaults={"value": value},
    )

    # Если лайк уже существовал, обновляем значение
    if not created:
        # Если пользователь пытается поставить тот же лайк, удаляем его
        if like.value == value:
            like.delete()
            question_obj.refresh_from_db()
            return JsonResponse({"rating": question_obj.rating, "removed": True})
        # Иначе обновляем значение
        like.value = value
        like.save()

    question_obj.refresh_from_db()
    return JsonResponse({"rating": question_obj.rating, "removed": False})


@login_required(login_url="/login/")
@require_http_methods(["POST"])
def like_answer(request: HttpRequest) -> JsonResponse:
    """AJAX обработчик для лайка/дизлайка ответа"""
    try:
        answer_id = int(request.POST.get("answer_id", 0))
        value = int(request.POST.get("value", 0))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Неверные параметры запроса"}, status=400)

    if value not in [-1, 1]:
        return JsonResponse({"error": "Значение должно быть -1 или 1"}, status=400)

    try:
        answer_obj = Answer.objects.get(id=answer_id)
    except Answer.DoesNotExist:
        return JsonResponse({"error": "Ответ не найден"}, status=404)

    # Получаем или создаем лайк
    like, created = AnswerLike.objects.get_or_create(
        user=request.user,
        answer=answer_obj,
        defaults={"value": value},
    )

    # Если лайк уже существовал, обновляем значение
    if not created:
        # Если пользователь пытается поставить тот же лайк, удаляем его
        if like.value == value:
            like.delete()
            answer_obj.refresh_from_db()
            return JsonResponse({"rating": answer_obj.rating, "removed": True})
        # Иначе обновляем значение
        like.value = value
        like.save()

    answer_obj.refresh_from_db()
    return JsonResponse({"rating": answer_obj.rating, "removed": False})


@login_required(login_url="/login/")
@require_http_methods(["POST"])
def mark_correct_answer(request: HttpRequest) -> JsonResponse:
    """AJAX обработчик для отметки правильного ответа"""
    try:
        question_id = int(request.POST.get("question_id", 0))
        answer_id = int(request.POST.get("answer_id", 0))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Неверные параметры запроса"}, status=400)

    try:
        question_obj = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return JsonResponse({"error": "Вопрос не найден"}, status=404)

    # Проверка авторства вопроса
    if question_obj.author != request.user:
        return JsonResponse(
            {"error": "Только автор вопроса может отметить правильный ответ"}, status=403
        )

    try:
        answer_obj = Answer.objects.get(id=answer_id, question=question_obj)
    except Answer.DoesNotExist:
        return JsonResponse(
            {"error": "Ответ не найден или не принадлежит этому вопросу"}, status=404
        )

    # Получаем значение чекбокса
    is_correct = request.POST.get("is_correct", "false").lower() == "true"

    if is_correct:
        # Сбрасываем все другие ответы на этот вопрос
        Answer.objects.filter(question=question_obj).exclude(id=answer_id).update(is_correct=False)
        # Устанавливаем текущий ответ как правильный
        answer_obj.is_correct = True
        answer_obj.save(update_fields=["is_correct"])
        return JsonResponse({"success": True, "is_correct": True})
    else:
        # Снимаем отметку
        answer_obj.is_correct = False
        answer_obj.save(update_fields=["is_correct"])
        return JsonResponse({"success": True, "is_correct": False})
