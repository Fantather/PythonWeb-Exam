from django.db import models
class TopicQuerySet(models.QuerySet):
    def active(self):
        """Возвращает активные Topics"""
        return self.filter(is_closed=False)
    
    def pinned_first(self):
        """Возвращает сначала закреплённые Topics, а потом сортирует по дате последней активности в Topic"""
        return self.filter('-is_pinned', '-last_active')
        
    
class PostQuerySet(models.QuerySet):
    """Менеджер для работы с постами (комментариями)."""

    def get_thread(self, topic_id:int):
        """
        Извлекает Всё дерево обсуждения для конкретной темы одним запросом
        """

        return self.filter(
            topic_id=topic_id
        ).select_related(
            "author"
        ).order_by(
            "created_at"
        )
    
    def get_topic_starter(self, topic_id:int):
        """
        Извлекает только самый первый пост из Topic.
        Если понадобится preview для Topic вывести
        """

        return self.filter(topic_id=topic_id, parent__isnull=True).first()