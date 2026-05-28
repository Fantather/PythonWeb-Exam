from django.contrib.auth import get_user_model
from .models import Community, Topic, Post

def seedCategories():
    '''
    Временная функция для заполнения базы данными
    '''
    if not Community.objects.exists():
        for i in range(1, 10):
            Community.add_root(
                title=f"Категория {i}",
                description=f"Описание категории {i}",
                icon="catto.png"
            )

def clearCategories():
    '''
    Временная функция для очистки базы от данных
    '''
    Community.objects.all().delete()
    
def seedTopics():
    '''
    Временная функция для заполнения базы данными
    '''
    first_category = Community.objects.first()
    
    if not first_category:
        print("Ошибка: Нет ни одной категории. Сначала выполните seedCategories()")
        return

    User = get_user_model()
    author = User.objects.first()
    
    if not author:
        author = User.objects.create_user(
            username="seed_author", 
            email="seed@example.com", 
            password="password123"
        )

    topic_data = [
        {
            "title": f"Топик {i}",
            "category": first_category,
            "author": author
        }
        for i in range(1, 10)
    ]
    
    if not Topic.objects.exists():
        Topic.objects.bulk_create([Topic(**data) for data in topic_data])


def clearTopics():
    '''
    Временная функция для очистки базы от данных
    '''
    Topic.objects.all().delete()
