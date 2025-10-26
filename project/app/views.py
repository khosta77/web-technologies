from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .constants import ANSWERS_PER_PAGE, QUESTIONS_PER_PAGE
from .mockRepositories import (
    AnswerMockRepository,
    QuestionMockRepository,
    TagMockRepository,
    UserMockRepository,
)
from .utils import paginate


# Инициализация репозиториев
question_repository = QuestionMockRepository()
answer_repository = AnswerMockRepository()
tag_repository = TagMockRepository()
user_repository = UserMockRepository()


def get_authenticated_user(request: HttpRequest) -> dict[str, Any] | None:
    """Получить текущего авторизованного пользователя"""
    user_id = request.session.get("user_id")
    if user_id:
        return user_repository.get_user_by_id(user_id)  # type: ignore[no-any-return]
    return None


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница - список новых вопросов"""
    questions = question_repository.get_all_questions()
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    user = get_authenticated_user(request)
    return render(request, "index.html", {"page": page, "user": user})


def hot(request: HttpRequest) -> HttpResponse:
    """Список популярных вопросов"""
    questions = question_repository.get_hot_questions()
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    user = get_authenticated_user(request)
    return render(request, "index.html", {"page": page, "is_hot": True, "user": user})


def question(request: HttpRequest, question_id: int) -> HttpResponse:
    """Страница одного вопроса"""
    question_obj = question_repository.get_question_by_id(question_id)
    answers = answer_repository.get_answers_by_question_id(question_id)
    user = get_authenticated_user(request)

    page = paginate(answers, request, per_page=ANSWERS_PER_PAGE)
    return render(
        request,
        "question.html",
        {
            "question": question_obj,
            "page": page,
            "user": user,
        },
    )


def tag(request: HttpRequest, tag_name: str) -> HttpResponse:
    """Список вопросов по тегу"""
    questions = question_repository.get_questions_by_tag(tag_name)
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    user = get_authenticated_user(request)
    return render(request, "index.html", {"page": page, "tag_name": tag_name, "user": user})


def tags(request: HttpRequest) -> HttpResponse:
    """Страница списка тегов"""
    tags_list = tag_repository.get_all_tags()
    user = get_authenticated_user(request)
    return render(request, "tags.html", {"tags_list": tags_list, "user": user})


def login_view(request: HttpRequest) -> HttpResponse:
    """Форма авторизации"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = user_repository.authenticate(username, password)
        if user:
            request.session["user_id"] = user["id"]
            messages.success(request, f"Добро пожаловать, {username}!")
            next_url = request.GET.get("next", "/")
            return redirect(next_url)
        else:
            messages.error(request, "Неверное имя пользователя или пароль")

    return render(request, "login.html")


def signup(request: HttpRequest) -> HttpResponse:
    """Форма регистрации"""
    if request.method == "POST":
        # Пока просто редирект на главную (регистрация будет в ДЗ4)
        messages.info(request, "Регистрация будет реализована в ДЗ4")
        return redirect("index")

    user = get_authenticated_user(request)
    return render(request, "signup.html", {"user": user})


def ask(request: HttpRequest) -> HttpResponse:
    """Форма добавления вопроса"""
    user = get_authenticated_user(request)
    if not user:
        return redirect("login")

    return render(request, "ask.html", {"user": user})


def settings(request: HttpRequest) -> HttpResponse:
    """Страница настроек профиля"""
    user = get_authenticated_user(request)
    if not user:
        return redirect("login")

    if request.method == "POST":
        # Обновляем данные пользователя
        username = request.POST.get("username")
        email = request.POST.get("email")
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Обновляем username и email
        if username:
            user["username"] = username
        if email:
            user["email"] = email

        # Обработка смены пароля
        if current_password and new_password and confirm_password:
            # Проверяем текущий пароль
            if user.get("password") == current_password:
                if new_password == confirm_password:
                    user["password"] = new_password
                    messages.success(request, "Пароль успешно изменён")
                else:
                    messages.error(request, "Новые пароли не совпадают")
            else:
                messages.error(request, "Неверный текущий пароль")

        # В реальном приложении здесь будет сохранение в БД
        messages.success(request, "Профиль обновлён")

    # Получаем вопросы и ответы пользователя
    questions = user_repository.get_user_questions(user["id"])
    answers = user_repository.get_user_answers(user["id"])

    return render(
        request,
        "settings.html",
        {
            "user": user,
            "user_questions": questions,
            "user_answers": answers,
        },
    )


def profile(request: HttpRequest, user_id: int) -> HttpResponse:
    """Страница профиля пользователя"""
    user = get_authenticated_user(request)
    profile_user = user_repository.get_user_by_id(user_id)

    if not profile_user:
        messages.error(request, "Пользователь не найден")
        return redirect("index")

    # Получаем вопросы и ответы пользователя
    user_questions = user_repository.get_user_questions(user_id)
    user_answers = user_repository.get_user_answers(user_id)

    return render(
        request,
        "profile.html",
        {
            "user": user,
            "profile_user": profile_user,
            "user_questions": user_questions,
            "user_answers": user_answers,
        },
    )


def logout(request: HttpRequest) -> HttpResponse:
    """Выход из системы"""
    request.session.flush()
    messages.success(request, "Вы успешно вышли из системы")
    return redirect("index")
