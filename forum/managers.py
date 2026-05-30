from django.db import models
from django.db.models import F

class TopicQuerySet(models.QuerySet):
    """Менеджер для работы с темами форума."""

    def active(self) -> "TopicQuerySet":
        """Фильтрует QuerySet, оставляя только открытые темы."""
        return self.filter(is_closed=False)

    def newest(self) -> "TopicQuerySet":
        """Сортирует QuerySet по дате создания (по убыванию)."""
        return self.order_by('-created_at')

    def recently_active(self) -> "TopicQuerySet":
        """Сортирует QuerySet по дате последней активности (по убыванию)."""
        return self.order_by('-last_active')
    
    def pinned_first(self):
        """Возвращает сначала закреплённые Topics, а потом сортирует по дате последней активности в Topic."""
        return self.order_by('-is_pinned', '-last_active')
    
    def pinned(self) -> "TopicQuerySet":
        """Возвращает только закрепленные Topics."""
        return self.filter(is_pinned=True)
    
    def get_for_category(self, category_slug: str):
        """
        Возвращает список Topic для конкретной категории.
        Подтягивает категорию, которой принадлежит Topic.
        """
        return self.filter(
            category__slug=category_slug
        ).select_related(
            'category'
        ).order_by(
            "-is_pinned", "-last_active"
        )

    def get_by_user(self, user_id: int):
        """
        Возвращает все темы, созданные конкретным пользователем.
        """
        return self.filter(
            author_id=user_id
        ).order_by('-created_at')
    
    def increment_views(self, topic_id: int) -> int:
        """
        Атомарно увеличивает счетчик просмотров топика на 1.
        Возвращает количество обновленных строк (0 или 1).
        """
        return self.filter(pk=topic_id).update(views_count=F('views_count') + 1)

        
    
class PostQuerySet(models.QuerySet):
    """Менеджер для работы с Post."""

    def thread(self, topic_id:int):
        """
        Извлекает Всё дерево обсуждения для конкретной темы одним запросом.
        Подтягивает автора Post.
        """
        return self.filter(
            topic_id=topic_id
        ).select_related(
            "author", 
            "parent", 
            "parent__author"
        ).prefetch_related(
            "images"
        ).order_by("created_at")
    
    def get_topic_starter(self, topic_id:int):
        """
        Извлекает корневой пост темы.
        Если понадобится preview для Topic вывести.
        """

        return self.filter(
            topic_id=topic_id,
            parent__isnull=True
        ).first()
    
    def get_by_user(self, user_id:int):
        """
        Получаем все посты написанные пользователем.
        Подтягиваю так же Topic, что бы мы могли указать, в какой теме пользователь писал что-то.
        """
        return self.filter(
            author_id=user_id
        ).select_related(
            'topic'
        ).order_by('-created_at')