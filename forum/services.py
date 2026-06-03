from django.utils import timezone
from .models import Community, Post, Topic, PostImage
from django.db import transaction
from django.db.models import F
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import File

User = get_user_model()

class CommunityService:
    @classmethod
    @transaction.atomic
    def create_root_community(
        cls, 
        title: str, 
        owner: 'User', 
        slug: str | None = None, 
        description: str = "", 
        icon: str | File | None = None
    ) -> 'Community':
        """
        Атомарно создаёт корневое сообщество и подписывает на него создателя.
        """
        if not title.strip():
            raise ValidationError("Название сообщества не может быть пустым.")

        node_kwargs = {
            "title": title.strip(),
            "description": description.strip(),
            "owner": owner,
            "icon": icon,
        }
        
        if slug:
            node_kwargs["slug"] = slug.strip()

        community = Community.add_root(**node_kwargs)
        community.subscribers.add(owner) 

        return community

    # Не трогай только
    @staticmethod
    def create_subcommunity(parent: Community, title: str, owner: User, slug: str = "", description: str = "", icon: str = None) -> Community:
        """Добавляет дочерний узел к существующему сообществу."""
        community = parent.add_child(
            title=title,
            slug=slug,
            description=description,
            owner=owner,
            icon=icon,
        )
        community.subscribers.add(owner)
        return community
    

class TopicService:
    @classmethod
    @transaction.atomic
    def create_topic_with_post(
        cls,
        community: 'Community',
        author: 'User',
        title: str,
        content: str,
        images: list | str | None = None
    ) -> 'Topic':
        """
        Атомарно создает новую тему и корневое сообщение для нее.
        """
        if not title.strip():
            raise ValidationError("Заголовок темы не может быть пустым.")
        if not content.strip() and not images:
            raise ValidationError("Тема должна содержать текст первого сообщения или изображение.")
        
        topic = Topic.objects.create(
            community=community,
            author=author,
            title=title.strip(),
        )

        post = Post.objects.create(
            topic=topic,
            author=author,
            content=content.strip(),
            parent=None,
        )

        if images:
            if not isinstance(images, list):
                images = [images]
                
            for img in images:
                PostImage.objects.create(
                    post=post,
                    image=img
                )

        return topic


class PostService:
    @classmethod
    @transaction.atomic
    def create_reply(
        cls,
        topic: Topic,
        author: User,
        content: str,
        parent: Post,
        images: list | str | None = None
    ) -> Post:
        """
        Создает новый пост-ответ в теме и атомарно обновляет метрики темы.
        """
        if not content.strip() and not images:
            raise ValidationError("Сообщение не может быть пустым. Добавьте текст или изображение.")
        if topic.is_closed:
            raise ValidationError("Нельзя писать в закрытую тему.")
        
        post = Post.objects.create(
            topic=topic,
            author=author,
            content=content.strip(),
            parent=parent,
        )

        if images:
            if not isinstance(images, list):
                images = [images]
                
            for img in images:
                PostImage.objects.create(
                    post=post,
                    image=img
                )

        Topic.objects.filter(pk=topic.pk).update(
            replies_count=F('replies_count') + 1,
            last_active=timezone.now()
        )

        return post

    @classmethod
    @transaction.atomic
    def delete_post(cls, post: Post) -> str | None:
        """
        Удаляет пост. Если пост корневой (нет родителя) - удаляет всю тему.
        Возвращает URL для редиректа (если тема удалена) или None (если удален только коммент).
        """
        topic = post.topic
        
        if post.parent is None:
            redirect_url = topic.community.get_absolute_url()
            topic.delete() # Каскадно удалит все посты и картинки
            return redirect_url
            
        else:
            post.delete()
            Topic.objects.filter(pk=topic.pk).update(
                replies_count=F('replies_count') - 1
            )
            return None
        

    @classmethod
    @transaction.atomic
    def toggle_like(cls, post, user) -> bool:
        """
        Ставит или убирает лайк пользователя на посте.
        Возвращает True, если лайк поставлен, и False, если убран.
        """
        # Если пользователь уже лайкал пост - убираем лайк
        if post.liked_by.filter(id=user.id).exists():
            post.liked_by.remove(user)
            post.likes_count = F('likes_count') - 1
            post.save(update_fields=['likes_count'])
            return False
        
        # Если не лайкал - ставим
        else:
            post.liked_by.add(user)
            post.likes_count = F('likes_count') + 1
            post.save(update_fields=['likes_count'])
            return True