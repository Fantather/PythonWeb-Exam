from core.models import User
from forum.models import Category, Post
from django.db import transaction
from django.db.models import F

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
                Post.objects.filter(id=user.pk).update(likes_count=F('likes_count')-1)
                return False
            
            post.liked_by.add(user)
            Post.objects.filter(id=post.pk).update(likes_count=F('likes_count')+1)
            return True