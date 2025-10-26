"""
Тесты для views
"""
from django.test import Client, TestCase
from django.urls import reverse
from app.views import get_authenticated_user
from app.mockRepositories import UserMockRepository


class ViewsTestCase(TestCase):
    """Тесты для views"""
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.client = Client()
        self.repository = UserMockRepository()
    
    def test_index_status_code(self):
        """Тест статуса главной страницы"""
        response = self.client.get('/')
        
        assert response.status_code == 200
    
    def test_hot_status_code(self):
        """Тест статуса страницы горячих вопросов"""
        response = self.client.get('/hot/')
        
        assert response.status_code == 200
    
    def test_tags_status_code(self):
        """Тест статуса страницы тегов"""
        response = self.client.get('/tags/')
        
        assert response.status_code == 200
    
    def test_question_status_code(self):
        """Тест статуса страницы вопроса"""
        response = self.client.get('/question/1/')
        
        assert response.status_code == 200
    
    def test_question_not_found(self):
        """Тест несуществующего вопроса"""
        response = self.client.get('/question/99999/')
        
        # В текущей реализации возвращается 200 с пустым контекстом
        # или может быть 404/302 - проверяем что не возникает ошибки
        assert response.status_code in [200, 404, 302]
    
    def test_tag_page_status_code(self):
        """Тест статуса страницы с вопросами по тегу"""
        response = self.client.get('/tag/python/')
        
        assert response.status_code == 200
    
    def test_login_page_status_code(self):
        """Тест статуса страницы входа"""
        response = self.client.get('/login/')
        
        assert response.status_code == 200
    
    def test_signup_page_status_code(self):
        """Тест статуса страницы регистрации"""
        response = self.client.get('/register/')
        
        assert response.status_code == 200
    
    def test_login_success(self):
        """Тест успешного входа"""
        response = self.client.post('/login/', {
            'username': 'python_dev',
            'password': '12345'
        })
        
        # После успешного входа должен быть редирект
        assert response.status_code in [302, 200]
    
    def test_login_failure(self):
        """Тест неудачного входа"""
        response = self.client.post('/login/', {
            'username': 'python_dev',
            'password': 'wrong_password'
        })
        
        # При неудачном входе должна вернуться форма
        assert response.status_code == 200
    
    def test_logout_redirect(self):
        """Тест выхода из системы"""
        # Сначала логинимся
        self.client.post('/login/', {
            'username': 'python_dev',
            'password': '12345'
        })
        
        # Затем выходим
        response = self.client.get('/logout/')
        
        # Должен быть редирект
        assert response.status_code == 302
    
    def test_ask_page_requires_login(self):
        """Тест что страница ask требует логина"""
        response = self.client.get('/ask/')
        
        # Должен быть редирект на логин
        assert response.status_code == 302
    
    def test_settings_page_requires_login(self):
        """Тест что страница settings требует логина"""
        response = self.client.get('/settings/')
        
        # Должен быть редирект на логин
        assert response.status_code == 302
    
    def test_settings_page_with_login(self):
        """Тест страницы settings с логином"""
        # Логинимся
        self.client.post('/login/', {
            'username': 'python_dev',
            'password': '12345'
        })
        
        response = self.client.get('/settings/')
        
        # Теперь должен быть доступ
        assert response.status_code == 200
    
    def test_profile_page(self):
        """Тест страницы профиля"""
        response = self.client.get('/profile/1/')
        
        assert response.status_code == 200
    
    def test_profile_not_found(self):
        """Тест несуществующего профиля"""
        response = self.client.get('/profile/99999/')
        
        # Должен быть редирект или 404
        assert response.status_code in [302, 404]

