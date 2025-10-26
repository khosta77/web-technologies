"""
Context processors для Django
"""
from django.contrib import auth


def user_context(request):
    """Добавляет текущего пользователя в контекст всех шаблонов"""
    from .mockRepositories.user_mock_repository import UserMockRepository
    
    # Создаем экземпляр репозитория для получения пользователя
    repo = UserMockRepository()
    
    user_id = request.session.get('user_id')
    user = None
    if user_id:
        user = repo.get_user_by_id(user_id)
    
    return {'user': user}

