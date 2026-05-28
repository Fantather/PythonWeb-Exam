from django.utils import timezone
from .models import Community, Post, Topic
from django.db import transaction
from django.db.models import F
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

User = get_user_model()

class CommunityService:
    @staticmethod
    def create_root_community(title: str, slug: str, owner: User, description: str = "") -> Community:
        """Создаёт корневой узел."""
        return Community.add_root(
            title=title,
            slug=slug,
            description=description,
            owner=owner
        )
    
    @staticmethod
    def create_subcommunity(parent: Community, title: str, slug: str, owner: User, description: str = "") -> Community:
        """Добавляет дочерний узел к существующему сообществу."""
        return parent.add_child(
            title=title,
            slug=slug,
            description=description,
            owner=owner
        )
    

class TopicService:
    @classmethod
    @transaction.atomic
    def create_topic_with_post(
        cls,
        community: Community,
        author: User,
        title: str,
        content: str,
        image: UploadedFile | str | None = None
    ) -> Topic:
        """
        Атомарно создает новую тему и корневое сообщение для нее.
        """
        if not title.strip():
            raise ValidationError("Заголовок темы не может быть пустым.")
        if not content.strip():
            raise ValidationError("Текст первого сообщения не может быть пустым.")
        
        topic = Topic.objects.create(
            community=community,
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
            if post.liked_by.filter(id=user.pk).exists():
                post.liked_by.remove(user)
                Post.objects.filter(id=post.pk).update(likes_count=F('likes_count') - 1)
                return False
            
            post.liked_by.add(user)
            Post.objects.filter(id=post.pk).update(likes_count=F('likes_count') + 1)
            return True
        

    @classmethod
    @transaction.atomic
    def create_reply(
        cls,
        topic: Topic,
        author: User,
        content: str,
        parent: Post,
        image: UploadedFile | str | None = None
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