"""
Репозиторий для работы с тегами через Django ORM
"""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from app.interfaces import ITagRepository
from app.models import Tag


class TagRepository(ITagRepository):
    """Реализация интерфейса ITagRepository с использованием Django ORM"""

    def get_all_tags(self) -> QuerySet:
        """Получить все теги"""
        return Tag.objects.all()

    def get_tag_info(self, tag_name: str) -> dict[str, Any]:
        """Получить информацию о теге"""
        try:
            tag = Tag.objects.get(name=tag_name)
            questions_count = tag.questions.count()

            # Получаем связанные теги (теги, которые часто встречаются вместе с этим)
            related_tags = (
                Tag.objects.filter(questions__tags=tag)
                .exclude(name=tag_name)
                .distinct()
                .values_list("name", flat=True)[:5]
            )

            return {
                "name": tag.name,
                "questions_count": questions_count,
                "related_tags": list(related_tags),
            }
        except Tag.DoesNotExist:
            return {
                "name": tag_name,
                "questions_count": 0,
                "related_tags": [],
            }
