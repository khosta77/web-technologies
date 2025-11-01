"""
Константы приложения AskPupkin
"""

# Количество элементов на странице
# Количество вопросов, отображаемых на одной странице в списке вопросов
QUESTIONS_PER_PAGE = 7
# Количество ответов, отображаемых на одной странице в списке ответов
ANSWERS_PER_PAGE = 20

# Количество генерируемых заглушек
# Количество вопросов-заглушек, которые генерируются для тестирования
MOCK_QUESTIONS_COUNT = 30
# Количество ответов-заглушек, которые генерируются для одного
# вопроса при тестировании (для каждого вопроса генерируется 10 ответов)
MOCK_ANSWERS_COUNT = 10

# Список тегов, которые генерируются для тестирования
MOCK_TAGS_LIST = [
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
]

# URL маршруты для разных типов лент
RATING_SORT_ORDER_ASC = "asc"
RATING_SORT_ORDER_DESC = "desc"
