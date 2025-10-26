"""
Тесты для context processors
"""

from django.test import RequestFactory

from app.context_processors import user_context


class ContextProcessorsTestCase:
    """Тесты для context processors"""

    def test_user_context_without_session(self):
        """Тест контекста без сессии"""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        context = user_context(request)

        assert "user" in context
        assert context["user"] is None
        assert "best_members" in context
        assert len(context["best_members"]) > 0

    def test_user_context_with_session(self):
        """Тест контекста с сессией"""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {"user_id": 1}

        context = user_context(request)

        assert "user" in context
        assert context["user"] is not None
        assert context["user"]["id"] == 1
        assert context["user"]["username"] == "python_dev"
        assert "best_members" in context

    def test_user_context_with_invalid_session(self):
        """Тест контекста с невалидным ID в сессии"""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {"user_id": 99999}

        context = user_context(request)

        assert "user" in context
        assert context["user"] is None
        assert "best_members" in context

    def test_best_members_in_context(self):
        """Тест наличия best_members в контексте"""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        context = user_context(request)

        assert "best_members" in context
        assert len(context["best_members"]) == 5
        # Проверяем что отсортированы по рейтингу
        ratings = [u["rating"] for u in context["best_members"]]
        assert ratings == sorted(ratings, reverse=True)

    def test_best_members_has_correct_fields(self):
        """Тест что best_members содержит правильные поля"""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        context = user_context(request)

        for member in context["best_members"]:
            assert "id" in member
            assert "username" in member
            assert "rating" in member
            assert "email" in member
