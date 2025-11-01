from __future__ import annotations

from typing import Any

from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.http import HttpRequest


def paginate(objects_list: list[Any], request: HttpRequest, per_page: int = 10) -> Page[Any]:
    """
    Функция для пагинации объектов.

    Args:
        objects_list: список объектов для пагинации
        request: объект запроса Django
        per_page: количество объектов на странице (по умолчанию 10)

    Returns:
        page: объект страницы пагинатора
    """
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get("page", 1)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page
