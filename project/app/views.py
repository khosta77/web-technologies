from django.shortcuts import render
from .utils import paginate
from .constants import QUESTIONS_PER_PAGE, ANSWERS_PER_PAGE
from .mockRepositories import (
    QuestionMockRepository,
    AnswerMockRepository,
    TagMockRepository
)

# Инициализация репозиториев
question_repository = QuestionMockRepository()
answer_repository = AnswerMockRepository()
tag_repository = TagMockRepository()


def index(request):
    """Главная страница - список новых вопросов"""
    questions = question_repository.get_all_questions()
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    return render(request, 'index.html', {'page': page})


def hot(request):
    """Список популярных вопросов"""
    questions = question_repository.get_hot_questions()
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    return render(request, 'index.html', {'page': page, 'is_hot': True})


def question(request, question_id):
    """Страница одного вопроса"""
    question_obj = question_repository.get_question_by_id(question_id)
    answers = answer_repository.get_answers_by_question_id(question_id)
    
    page = paginate(answers, request, per_page=ANSWERS_PER_PAGE)
    return render(request, 'question.html', {
        'question': question_obj,
        'page': page,
    })


def tag(request, tag_name):
    """Список вопросов по тегу"""
    questions = question_repository.get_questions_by_tag(tag_name)
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    return render(request, 'index.html', {'page': page, 'tag_name': tag_name})


def tags(request):
    """Страница списка тегов"""
    tags_list = tag_repository.get_all_tags()
    return render(request, 'tags.html', {'tags_list': tags_list})


def login_view(request):
    """Форма авторизации"""
    return render(request, 'login.html')


def signup(request):
    """Форма регистрации"""
    return render(request, 'signup.html')


def ask(request):
    """Форма добавления вопроса"""
    return render(request, 'ask.html')


def settings(request):
    """Страница настроек профиля"""
    return render(request, 'settings.html')
