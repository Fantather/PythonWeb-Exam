from django.utils import timezone
from core.models import User
from .models import Category, Post, Topic
from django.db import transaction
from django.db.models import F
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

class CategoryServise:
    @staticmethod
    def create_root_category(title: str, slug: str, description: str = "") -> Category:
        """Создаёт корневой узел"""
        return Category.add_root(
            title=title,
            slug=slug,
            description=description,
        )
    
    @staticmethod
    def create_subcategory(parent: Category, title: str, slug: str, description = "") -> Category:
        """Добавляет дочерний узел к существующей категории."""
        return parent.add_child(
            title=title,
            slug=slug,
            description=description,
        )
    

class TopicService:
    @classmethod
    @transaction.atomic
    def create_topic_with_post(
        cls,
        category:Category,
        author:User,
        title:str,
        content:str,
        image: UploadedFile | None = None
    ) -> Topic:
        """
        Атомарно создает новую тему и корневое сообщение для нее.
        """

        if not title.strip():
            raise ValidationError("Заголовок темы не может быть пустым.")
        if not content.strip():
            raise ValidationError("Текст первого сообщения не может быть пустым.")
        
        topic = Topic.objects.create(
            category=category,
            author=author,
            title=title.strip(),
        )

        Post.objects.create(
            topic=topic,
            author=author,
            content=content.strip(),
            parent=None,
            image=image,
        )

        return topic

    

class PostService:
    @staticmethod
    def toggle_like(post: Post, user: User) -> bool:
        """
        Управляет состоянием лайка. 
        Возвращает True, если связь создана, False - если удалена.
        """
        with transaction.atomic():
            if post.liked_by.filter(id=post.pk).exists():
                post.liked_by.remove(user)
                Post.objects.filter(id=user.pk).update(likes_count=F('likes_count')-1)
                return False
            
            post.liked_by.add(user)
            Post.objects.filter(id=post.pk).update(likes_count=F('likes_count')+1)
            return True
        

    @classmethod
    @transaction.atomic
    def create_reply(
        cls,
        topic: Topic,
        author: User,
        content: str,
        parent: Post,
        image: UploadedFile|None = None
    ) -> Post:
        """
        Создает новый пост-ответ в теме и атомарно обновляет метрики темы.
        """

        if not content.strip():
            raise ValidationError("Сообщение не может быть пустым.")
        if topic.is_closed:
            raise ValidationError("Нельзя писать в закрытую тему.")
        
        post = Post.objects.create(
            topic=topic,
            author=author,
            content=content.strip(),
            parent=parent,
            image=image
        )

        Topic.objects.filter(pk=topic.pk).update(
            replies_count=F('replies_count') + 1,
            last_active=timezone.now()
        )

        return post