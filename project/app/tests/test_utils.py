"""
Тесты для утилит
"""

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from app.utils import paginate


class TestPaginate:
    """Тесты для функции paginate"""

    def test_paginate_basic(self):
        """Тест базовой пагинации с первой страницей"""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()

        objects = list(range(1, 26))  # 25 объектов
        result = paginate(objects, request, per_page=10)

        assert result.has_other_pages()
        assert result.number == 1
        assert len(result.object_list) == 10
        assert list(result.object_list) == list(range(1, 11))

    def test_paginate_second_page(self):
        """Тест пагинации со второй страницей"""
        factory = RequestFactory()
        request = factory.get("/?page=2")
        request.user = AnonymousUser()

        objects = list(range(1, 26))
        result = paginate(objects, request, per_page=10)

        assert result.number == 2
        assert len(result.object_list) == 10
        assert list(result.object_list) == list(range(11, 21))

    def test_paginate_empty_page(self):
        """Тест пустой страницы - должна вернуться последняя"""
        factory = RequestFactory()
        request = factory.get("/?page=999")
        request.user = AnonymousUser()

        objects = list(range(1, 26))
        result = paginate(objects, request, per_page=10)

        assert result.number == 3  # Последняя страница
        assert len(result.object_list) == 5  # Последние 5 объектов

    def test_paginate_invalid_page(self):
        """Тест невалидного номера страницы - должно вернуться 1"""
        factory = RequestFactory()
        request = factory.get("/?page=abc")
        request.user = AnonymousUser()

        objects = list(range(1, 26))
        result = paginate(objects, request, per_page=10)

        assert result.number == 1
        assert list(result.object_list) == list(range(1, 11))

    def test_paginate_single_page(self):
        """Тест пагинации когда все помещается на одну страницу"""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()

        objects = list(range(1, 6))
        result = paginate(objects, request, per_page=10)

        assert not result.has_other_pages()
        assert result.number == 1
        assert len(result.object_list) == 5

    def test_paginate_empty_list(self):
        """Тест пагинации пустого списка"""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()

        objects = []
        result = paginate(objects, request, per_page=10)

        assert result.number == 1
        assert len(result.object_list) == 0

    def test_paginate_custom_per_page(self):
        """Тест пагинации с кастомным количеством на странице"""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()

        objects = list(range(1, 26))
        result = paginate(objects, request, per_page=5)

        assert result.paginator.per_page == 5
        assert len(result.object_list) == 5
        assert result.paginator.num_pages == 5
