"""
Mock данные для пользователей
"""

# Заглушки для пользователей
MOCK_USERS = [
    {
        "id": 1,
        "username": "python_dev",
        "password": "12345",
        "email": "dev@example.com",
        "avatar": "img/avatar1.jpg",
        "rating": 245,
        "questions_count": 15,
        "answers_count": 43,
    },
    {
        "id": 2,
        "username": "django_master",
        "password": "12345",
        "email": "master@example.com",
        "avatar": "img/avatar.jpg",
        "rating": 567,
        "questions_count": 8,
        "answers_count": 129,
    },
    {
        "id": 3,
        "username": "react_expert",
        "password": "12345",
        "email": "expert@example.com",
        "avatar": "img/avatar.jpg",
        "rating": 892,
        "questions_count": 23,
        "answers_count": 234,
    },
    {
        "id": 4,
        "username": "git_guru",
        "password": "12345",
        "email": "guru@example.com",
        "avatar": "img/avatar.jpg",
        "rating": 1204,
        "questions_count": 3,
        "answers_count": 456,
    },
    {
        "id": 5,
        "username": "database_expert",
        "password": "12345",
        "email": "expert@database.com",
        "avatar": "img/avatar.jpg",
        "rating": 345,
        "questions_count": 12,
        "answers_count": 67,
    },
]


def get_user_by_username(username):
    """Найти пользователя по username"""
    for user in MOCK_USERS:
        if user["username"] == username:
            return user
    return None


def authenticate_user(username, password):
    """Проверить логин и пароль"""
    user = get_user_by_username(username)
    if user and user["password"] == password:
        return user
    return None


def get_user_by_id(user_id):
    """Найти пользователя по ID"""
    for user in MOCK_USERS:
        if user["id"] == user_id:
            return user
    return None


def get_user_questions(user_id):
    """Получить вопросы пользователя"""
    # Импортируем локально чтобы избежать циклических зависимостей
    from app.mockRepositories.mock_data_frames import NEW_QUESTIONS

    # Возвращаем первые 5 вопросов как пример
    questions = NEW_QUESTIONS[:5].copy()
    for q in questions:
        q["author_id"] = user_id
        q["author"] = "you"
    return questions


def get_user_answers(user_id):
    """Получить ответы пользователя"""
    # Возвращаем примеры ответов
    from app.mockRepositories.mock_data_frames import SAMPLE_ANSWERS

    answers = SAMPLE_ANSWERS.copy()
    for a in answers:
        a["author_id"] = user_id
        a["author"] = "you"
    return answers
