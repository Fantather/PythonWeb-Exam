import uuid
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from unidecode import unidecode
from treebeard.mp_tree import MP_Node

from core.models import TimeStampedModel
from forum.managers import PostQuerySet, TopicQuerySet


class Community(MP_Node, TimeStampedModel):
    """
    короче это сообщество. 
    Модели:
     - title - название категории
     - slug - уникальный идентификатор для URL
     - description - описание категории
     - node_order_by - порядок сортировки узлов (по названию)
     - owner - владелец сообщества (пользователь, который его создал)
     - subscribers - подписчики сообщества (пользователи, которые подписались на обновления сообщества)
     - icon - иконка сообщества (опционально, может быть загружена пользователем)
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_communities",
        verbose_name=_("Owner")
    )
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="subscibed_comunities",
        blank=True,
        verbose_name=_("Subscribers"),
    )
    title = models.CharField(
        max_length=255, 
        verbose_name=_("Title")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_("Slug")
    )
    description = models.TextField(
        blank=True, 
        verbose_name=_("Description")
    )
    icon = models.FileField(
        upload_to="icons/",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['svg', 'png', 'webp', 'jpg', 'jpeg'])],
        verbose_name=_("Icon")
    )
    node_order_by = ["title"]

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("Community")
        verbose_name_plural = _("Communities")
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs) -> None:
        """Добавляем генерацию slug"""
        if not self.slug:
            base_slug = slugify(unidecode(self.title)) or 'community'
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('community_detail', kwargs={
            'community_id': self.pk, 
            'slug': self.slug
        })




class Topic(TimeStampedModel):
    """
    Топик - главная тема для обсуждения, которая может содержать в себе посты (сообщения)
    Модели:
     - community - сообщество, к которому относится топик
     - title - название топика
     - is_closed - флаг, указывающий, закрыт ли топик для новых сообщений
     - is_pinned - флаг, указывающий, закреплен ли топик в сообществе. По задумке, админы могут закреплять темы (Topics). Они будут обходить стандартную фильтрацию по дате последней активности и выводиться в самом верху
     - views_count - количество просмотров топика
     - replies_count - количество ответов в топике
     - last_active - дата и время последней активности в топике (создание или обновление поста)
    """
    community = models.ForeignKey(
        "forum.Community",
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name=_("Community")
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_topics",
        verbose_name=_("Author")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title")
    )
    is_closed = models.BooleanField(
        default=False,
        verbose_name=_("Is closed")
    )
    is_pinned = models.BooleanField(
        default=False,
        verbose_name=_("Is pinned")
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Views count")
    )
    replies_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Replies count")
    )
    last_active = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_("Last active")
    )
    
    objects = TopicQuerySet.as_manager()

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
        indexes = [
            models.Index(fields=["community", "-is_pinned", "-last_active"]),
        ]

    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self) -> str:
        """
        Позволяем получить полную ссылку на конкретный topic, включающую slug
        """
        slug_text = slugify(unidecode(self.title)) or "topic"
        return reverse("topic_detail", kwargs={
            "topic_id": self.pk,
            "slug": slug_text,
        })
    
    # Метод для получения ссылки на удаление
    def get_delete_url(self):
        return reverse('topic_delete', kwargs={'pk': self.pk})

    # Метод для получения ссылки на редактирование
    def get_update_url(self):
        return reverse('topic_update', kwargs={'pk': self.pk})

    # Свойство для генерации ID для HTML-циклов
    @property
    def dom_id(self):
        return f"topic-{self.pk}"


class Post(TimeStampedModel):
    """
    Пост - это сообщение в топике. Он может быть как начальным сообщением (постом-родителем), так и ответом на другой пост (постом-ребенком).
    Модель:
     - topic - тема, к которой относится пост
     - author - автор поста
     - parent - родительский пост (если это ответ), вложенность не ограничена
     - content - содержимое поста
     - liked_by - пользователи, которым понравился пост
     - likes_count - количество лайков
     - images - изображения, прикрепленные к посту
    """
    topic = models.ForeignKey(
        "forum.Topic",
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Topic")
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Author")
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("Parent post")
    )
    content = models.TextField(
        blank=True,
        verbose_name=_("Content")
    )
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_posts",
        blank=True,
        verbose_name=_("Liked by")
    )
    likes_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name=_("Likes count")
    )
    objects = PostQuerySet.as_manager()

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ['-created_at']
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        indexes = [
            models.Index(fields=["topic", "parent", "created_at"]),
        ]
    
    def __str__(self) -> str:
        return f"Post {self.pk} in Topic {self.topic_id}"
    
    
    def get_absolute_url(self) -> str:
        """Возвращает прямую ссылку на пост внутри ветки обсуждения темы."""
        return f"{self.topic.get_absolute_url()}#post-{self.pk}"

    # Метод для получения ссылки на удаление
    def get_delete_url(self):
        return reverse('post_delete', kwargs={'post_id': self.pk})

    # Метод для получения ссылки на редактирование
    def get_update_url(self):
        return reverse('post_update', kwargs={'post_id': self.pk})

    # Свойство для генерации ID для HTML-циклов
    @property
    def dom_id(self):
        return f"post-{self.pk}"


    def clean(self) -> None:
        """Валидация на уровне доменной модели."""
        if self.parent_id:
            parent_topic_id = Post.objects.filter(pk=self.parent_id).values_list('topic_id', flat=True).first()
            if parent_topic_id and self.topic_id != parent_topic_id:
                raise ValidationError({
                    'parent': _("Дочерний пост обязан принадлежать тому же Topic, что и родительский.")
                })
        super().clean()


class PostImage(TimeStampedModel):
    """
    Изображение, прикрепленное к посту.
    Модель:
     - post - пост, к которому относится изображение
     - image - файл изображения
    """
    post = models.ForeignKey(
        "forum.Post",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Post")
    )
    image = models.ImageField(
        upload_to="posts/images/%Y/%m/%d/",
        verbose_name=_("Image")
    )

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ['created_at']   # Сортировка по дате создания гарантирует вывод в порядке загрузки
        verbose_name = _("Post image")
        verbose_name_plural = _("Post images")

    def __str__(self) -> str:
        return f"Image for post ID {self.post_id}"