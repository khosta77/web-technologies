from django.shortcuts import render
from .utils import paginate


def index(request):
    """Главная страница - список новых вопросов"""
    questions = []
    for i in range(1, 31):
        questions.append({
            'id': i,
            'title': f'How to build a moon park {i}?',
            'text': f'Guys, i have trouble with a moon park {i}. Can\'t find th black-jack...',
            'author': f'user{i % 10}',
            'rating': i * 5,
            'answers_count': i % 5,
            'tags': ['python', 'django'] if i % 2 == 0 else ['javascript', 'react'],
        })
    
    page = paginate(questions, request, per_page=5)
    return render(request, 'index.html', {'page': page})


def hot(request):
    """Список популярных вопросов"""
    questions = []
    for i in range(1, 31):
        questions.append({
            'id': i,
            'title': f'Hot Question #{i}: Advanced Django Patterns',
            'text': f'This is a highly rated question about Django patterns {i}...',
            'author': f'expert{i % 5}',
            'rating': 1000 - i * 20,
            'answers_count': i % 15,
            'tags': ['django', 'python', 'best-practices'],
        })
    
    # Сортируем по рейтингу (убывание)
    questions.sort(key=lambda x: x['rating'], reverse=True)
    
    page = paginate(questions, request, per_page=5)
    return render(request, 'index.html', {'page': page, 'is_hot': True})


def question(request, question_id):
    """Страница одного вопроса"""
    question_obj = {
        'id': question_id,
        'title': f'How to build a moon park?',
        'text': 'Guys, i have trouble with a moon park. Can\'t find th black-jack...',
        'author': 'user123',
        'rating': 15,
        'answers_count': 3,
        'tags': ['black-jack', 'bender'],
    }
    
    answers = []
    for i in range(1, 10):
        answers.append({
            'id': i,
            'text': f'Answer {i}: This is a detailed answer to the question...',
            'author': f'helper{i}',
            'rating': 10 - i,
            'is_correct': i == 2,  # Второй ответ - правильный
        })
    
    page = paginate(answers, request, per_page=3)
    return render(request, 'question.html', {
        'question': question_obj,
        'page': page,
    })


def tag(request, tag_name):
    """Список вопросов по тегу"""
    questions = []
    for i in range(1, 21):
        questions.append({
            'id': i,
            'title': f'Question {i} about {tag_name}',
            'text': f'This question is related to {tag_name}. Detailed explanation...',
            'author': f'user{i % 10}',
            'rating': i * 10,
            'answers_count': i % 8,
            'tags': [tag_name],
        })
    
    page = paginate(questions, request, per_page=5)
    return render(request, 'index.html', {'page': page, 'tag_name': tag_name})


def tags(request):
    """Страница списка тегов"""
    tags_list = [
        'python', 'django', 'javascript', 'react', 'mysql', 'postgresql',
        'html', 'css', 'java', 'c++', 'web', 'programming'
    ]
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
