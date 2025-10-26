from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import paginate
from .constants import QUESTIONS_PER_PAGE, ANSWERS_PER_PAGE
from .mockRepositories import (
    QuestionMockRepository,
    AnswerMockRepository,
    TagMockRepository,
    UserMockRepository,
)

# Инициализация репозиториев
question_repository = QuestionMockRepository()
answer_repository = AnswerMockRepository()
tag_repository = TagMockRepository()
user_repository = UserMockRepository()


def get_authenticated_user(request):
    """Получить текущего авторизованного пользователя"""
    user_id = request.session.get('user_id')
    if user_id:
        return user_repository.get_user_by_id(user_id)
    return None


def index(request):
    """Главная страница - список новых вопросов"""
    questions = question_repository.get_all_questions()
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    user = get_authenticated_user(request)
    return render(request, 'index.html', {'page': page, 'user': user})


def hot(request):
    """Список популярных вопросов"""
    questions = question_repository.get_hot_questions()
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    user = get_authenticated_user(request)
    return render(request, 'index.html', {'page': page, 'is_hot': True, 'user': user})


def question(request, question_id):
    """Страница одного вопроса"""
    question_obj = question_repository.get_question_by_id(question_id)
    answers = answer_repository.get_answers_by_question_id(question_id)
    user = get_authenticated_user(request)
    
    page = paginate(answers, request, per_page=ANSWERS_PER_PAGE)
    return render(request, 'question.html', {
        'question': question_obj,
        'page': page,
        'user': user,
    })


def tag(request, tag_name):
    """Список вопросов по тегу"""
    questions = question_repository.get_questions_by_tag(tag_name)
    page = paginate(questions, request, per_page=QUESTIONS_PER_PAGE)
    user = get_authenticated_user(request)
    return render(request, 'index.html', {'page': page, 'tag_name': tag_name, 'user': user})


def tags(request):
    """Страница списка тегов"""
    tags_list = tag_repository.get_all_tags()
    user = get_authenticated_user(request)
    return render(request, 'tags.html', {'tags_list': tags_list, 'user': user})


def login_view(request):
    """Форма авторизации"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = user_repository.authenticate(username, password)
        if user:
            request.session['user_id'] = user['id']
            messages.success(request, f'Добро пожаловать, {username}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'login.html')


def signup(request):
    """Форма регистрации"""
    if request.method == 'POST':
        # Пока просто редирект на главную (регистрация будет в ДЗ4)
        messages.info(request, 'Регистрация будет реализована в ДЗ4')
        return redirect('index')
    
    user = get_authenticated_user(request)
    return render(request, 'signup.html', {'user': user})


def ask(request):
    """Форма добавления вопроса"""
    user = get_authenticated_user(request)
    if not user:
        return redirect('login')
    
    return render(request, 'ask.html', {'user': user})


def settings(request):
    """Страница настроек профиля"""
    user = get_authenticated_user(request)
    if not user:
        return redirect('login')
    
    if request.method == 'POST':
        # Обновляем данные пользователя
        username = request.POST.get('username')
        email = request.POST.get('email')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Обновляем username и email
        if username:
            user['username'] = username
        if email:
            user['email'] = email
        
        # Обработка смены пароля
        if current_password and new_password and confirm_password:
            # Проверяем текущий пароль
            if user.get('password') == current_password:
                if new_password == confirm_password:
                    user['password'] = new_password
                    messages.success(request, 'Пароль успешно изменён')
                else:
                    messages.error(request, 'Новые пароли не совпадают')
            else:
                messages.error(request, 'Неверный текущий пароль')
        
        # В реальном приложении здесь будет сохранение в БД
        messages.success(request, 'Профиль обновлён')
    
    # Получаем вопросы и ответы пользователя
    questions = user_repository.get_user_questions(user['id'])
    answers = user_repository.get_user_answers(user['id'])
    
    return render(request, 'settings.html', {
        'user': user,
        'user_questions': questions,
        'user_answers': answers,
    })


def logout(request):
    """Выход из системы"""
    request.session.flush()
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('index')
