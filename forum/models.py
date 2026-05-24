from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings
from django.urls import reverse
from unidecode import unidecode
from core.models import TimeStampedModel
from treebeard.mp_tree import MP_Node
from django.utils.text import slugify

from forum.managers import PostQuerySet, TopicQuerySet


class Category(MP_Node, TimeStampedModel):
    '''
    Категория - это верхний уровень организации контента на форуме. Она может содержать в себе несколько топиков (тем для обсуждения).

    Модели:
     - title - название категории
     - slug - уникальный идентификатор для URL
     - description - описание категории
     - node_order_by - порядок сортировки узлов (по названию)
    '''
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        unique=True,
    )
    description = models.TextField(blank=True)
    icon = models.FileField(
        upload_to="static/assets/icons/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['svg', 'png', 'webp'])],
    )
    node_order_by = ["title"]

    class Meta(MP_Node.Meta):   # type: ignore[override]  так нада
        verbose_name = "Category"
        verbose_name_plural = "Categories"

        indexes = [
            models.Index(fields=["slug"]),
        ]


    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        """Добавляем генерацию slug"""
        if not self.slug:
            base_slug = slugify(unidecode(self.title)) or 'category'

            # А эту переменную мы будем изменять, если slug уже занят
            unique_slug = base_slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)

class Topic(TimeStampedModel):
    '''
    Топик - главная тема для обсуждения, которая может содержать в себе посты (сообщения)
    Модели:
     - category - категория, к которой относится топик
     - title - название топика
     - is_closed - флаг, указывающий, закрыт ли топик для новых сообщений
     - is_pinned - флаг, указывающий, закреплен ли топик в категории. По задумке, админы могут закреплять темы (Topics). Они будут обходить стандартную фильтрацию по дате последней активности и выводиться в самом верху
     - views_count - количество просмотров топика
     - replies_count - количество ответов в топике
     - last_active - дата и время последней активности в топике (создание или обновление поста)

    '''
    category = models.ForeignKey(
        "forum.category",
        on_delete=models.CASCADE,
        related_name="topics",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_topics",
        verbose_name="Автор темы"
    )
    title = models.CharField(max_length=255)
    is_closed = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)
    last_active = models.DateTimeField(auto_now_add=True)
    
    objects = TopicQuerySet.as_manager()

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        
        indexes = [
            models.Index(fields=["category", "-is_pinned", "-last_active"]),
        ]


    def get_absolute_url(self):
        '''
        Позволяем получить полную ссылку на конкретный topic, включающую slug
        '''
        slug_text = slugify(unidecode(self.title)) or "topic"
        return reverse("topic_detail", kwargs={
            "topic_id": self.pk,
            "slug": slug_text,
        })
    



class Post(TimeStampedModel):
    '''
    Пост - это сообщение в топике. Он может быть как начальным сообщением (постом-родителем), так и ответом на другой пост (постом-ребенком).
    Модель:
     - topic - тема, к которой относится пост
     - author - автор поста
     - parent - родительский пост (если это ответ), вложенность не ограничена
     - content - содержимое поста
     - liked_by - пользователи, которым понравился пост
     - likes_count - количество лайков
     - image - изображение, прикрепленное к посту
    '''
    topic = models.ForeignKey(
        "forum.Topic",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    content = models.TextField()
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_posts",
        blank=True,
    )
    likes_count = models.IntegerField(
        default=0,
        db_index=True,
    )
    image = models.ImageField(
        upload_to="posts/images/%Y/%m/%d/",
        blank=True,
    )

    objects = PostQuerySet.as_manager()

    class Meta(TimeStampedModel.Meta):
        ordering = ['-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

        indexes = [
            models.Index(fields=["topic", "parent", "created_at"]),
        ]
    

    def __str__(self):
        return f"Post {self.pk} in Topic {self.topic_id}"

    def clean(self):
        """Валидация на уровне доменной модели."""
        if self.parent_id:
            if self.topic_id != self.parent.topic_id:
                raise ValidationError("Дочерний пост обязан принадлежать тому же Topic, что и родительский.")
        super().clean()