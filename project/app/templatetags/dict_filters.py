"""
Кастомные фильтры для работы со словарями в шаблонах Django
"""

from typing import Any

from django import template


register = template.Library()


@register.filter
def get_item(dictionary: dict[Any, Any] | None, key: Any) -> Any:
    """
    Получить значение из словаря по ключу

    Использование в шаблоне:
    {{ my_dict|get_item:my_key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
