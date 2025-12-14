"""
Тесты для context processors
"""

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase

from app.context_processors import user_context
from app.models import Profile


class ContextProcessorsTestCase(TestCase):
    """Тесты для context processors"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.factory = RequestFactory()
        # Создаем пользователей с профилями для тестирования best_members
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )
        self.user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="pass123"
        )
        # Создаем профили с разными рейтингами
        Profile.objects.create(user=self.user1, rating=100)
        Profile.objects.create(user=self.user2, rating=50)
        Profile.objects.create(user=self.user3, rating=25)

    def test_user_context_without_authentication(self):
        """Тест контекста без аутентификации"""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        context = user_context(request)

        assert "user" in context
        assert context["user"] is None
        assert "best_members" in context
        assert isinstance(context["best_members"], list)

    def test_user_context_with_authentication(self):
        """Тест контекста с аутентификацией"""
        request = self.factory.get("/")
        request.user = self.user1

        context = user_context(request)

        assert "user" in context
        assert context["user"] is not None
        assert context["user"] == self.user1
        assert isinstance(context["user"], User)
        assert context["user"].username == "user1"
        assert "best_members" in context

    def test_best_members_in_context(self):
        """Тест наличия best_members в контексте"""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        context = user_context(request)

        assert "best_members" in context
        assert isinstance(context["best_members"], list)
        # Проверяем что отсортированы по рейтингу (убывание)
        if len(context["best_members"]) > 1:
            ratings = [u.profile.rating for u in context["best_members"] if hasattr(u, "profile")]
            assert ratings == sorted(ratings, reverse=True)

    def test_best_members_has_user_objects(self):
        """Тест что best_members содержит User объекты"""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        context = user_context(request)

        for member in context["best_members"]:
            assert isinstance(member, User)
            assert hasattr(member, "id")
            assert hasattr(member, "username")
            assert hasattr(member, "email")
            # Проверяем что профиль загружен через select_related
            if hasattr(member, "profile"):
                assert member.profile is not None

    def test_best_members_limit(self):
        """Тест что best_members ограничен 5 элементами"""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        context = user_context(request)

        assert len(context["best_members"]) <= 5

    def test_best_members_skipped_on_login_page(self):
        """Тест что best_members пустой на странице логина"""
        request = self.factory.get("/login/")
        request.user = AnonymousUser()

        context = user_context(request)

        assert "best_members" in context
        assert context["best_members"] == []

    def test_best_members_skipped_on_signup_page(self):
        """Тест что best_members пустой на странице регистрации"""
        request = self.factory.get("/signup/")
        request.user = AnonymousUser()

        context = user_context(request)

        assert "best_members" in context
        assert context["best_members"] == []

    def test_best_members_skipped_on_register_page(self):
        """Тест что best_members пустой на странице регистрации (register)"""
        request = self.factory.get("/register/")
        request.user = AnonymousUser()

        context = user_context(request)

        assert "best_members" in context
        assert context["best_members"] == []

    def test_best_members_skipped_on_admin_page(self):
        """Тест что best_members пустой на странице админки"""
        request = self.factory.get("/admin/")
        request.user = AnonymousUser()

        context = user_context(request)

        assert "best_members" in context
        assert context["best_members"] == []

    def test_best_members_only_users_with_profiles(self):
        """Тест что best_members содержит только пользователей с профилями"""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        context = user_context(request)

        for member in context["best_members"]:
            assert hasattr(member, "profile")
            assert member.profile is not None
