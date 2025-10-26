from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(objects_list, request, per_page=10):
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
    page_number = request.GET.get('page', 1)
    
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page

