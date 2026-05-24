from tabnanny import verbose
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from treebeard.mp_tree import MP_Node

class Post(TimeStampedModel):
    title = models.CharField(max_length=300)
    image = models.ImageField(
        upload_to="posts/images/%Y/%m/%d/",
        blank=True,
    )
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_posts",
        blank=True,
    )
    likes_count = models.IntegerField(
        default=0,
        db_index=True,
    )
    text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    class Meta(TimeStampedModel.Meta):
        ordering = ['-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
    

    def __str__(self):
        return f"{self.title[:50]}..." if len(self.title) > 50 else self.title


class Topic(models.Model):
    category = models.ForeignKey(
        "forum.category",
        on_delete=models.CASCADE,
        related_name="topics",
    )
    topic = models.CharField(max_length=255)
    is_closed = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)


class Category(MP_Node, TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        unique=True,
    )
    description = models.TextField(blank=True)

    none_order_by = ["title"]

    class Meta(MP_Node.Meta):   # type: ignore[override]  так нада
        verbose_name = "Category"
        verbose_name_plural = "Categories"

        indexes = [
            models.Index(fields=["slug"]),
        ]


    def __str__(self) -> str:
        return self.title
    

class Comment(TimeStampedModel):
    post = models.ForeignKey(
        "forum.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    content = models.TextField()

    class Meta(TimeStampedModel.Meta):
        ordering = ["created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

        indexes = [
            models.Index(fields=["post", "parent", "created_at"]),
        ]

    
    def __str__(self):
        return f"Comment {self.pk}; on Post {self.post_id}"
    
    def clean(self):
        """Валидация на уровне доменной модели для предотвращения глубокой вложенности."""
        if self.parent_id:
            # Блокировка попытки ответить на ответ (предотвращение уровней > 1)
            if self.parent.parent_id is not None:
                raise ValidationError("Превышена максимальная глубина вложенности комментариев.")
            # Блокировка привязки комментария к другому посту
            if self.post_id != self.parent.post_id:
                raise ValidationError("Дочерний комментарий должен принадлежать тому же посту.")
        super().clean()