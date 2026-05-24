from django.db import models
class TopicQuerySet(models.QuerySet):
    def active(self):
        """Возвращает активные Topics"""
        return self.filter(is_closed=False)
    
    def pinned_first(self):
        """Возвращает сначала закреплённые Topics, а потом сортирует по дате последней активности в Topic"""
        return self.filter('-is_pinned', '-last_active')
        