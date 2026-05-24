from .models import Category, Topic, Post

def seedCategories():
    '''
    Временная функция для заполнения базы данными
    '''
    categ_data = [
        {
            "title": f"Категория {i}",
            "description": f"Описание категории {i}",
            "image": "https://placehold.co/600x400",
            "slug": f"category-{i}"
        }
        for i in range(1, 10)
    ]   
    
    if not Category.objects.exists():
        # Оптимизация: создание записей одним SQL-запросом
        Category.objects.bulk_create([Category(**data) for data in categ_data])
    
def clearCategories():
    '''
    Временная функция для очистки базы от данных
    '''
    Category.objects.all().delete()
    
def seedTopics():
    '''
    Временная функция для заполнения базы данными
    '''
    first_category = Category.objects.first()
    if not first_category:
        print("Ошибка: Нет ни одной категории. Сначала выполните seedCategories()")
        return

    topic_data = [
        {
            "title": f"Топик {i}",
            "description": f"Описание топика {i}",
            "image": "https://placehold.co/600x400",
            "slug": f"topic-{i}",
            "category": first_category
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


def seedPosts():
    '''
    Временная функция для заполнения базы данными
    '''
    first_topic = Topic.objects.first()
    if not first_topic:
        print("Ошибка: Нет ни одного топика. Сначала выполните seedTopics()")
        return

    post_data = [
        {
            "content": f"Содержимое поста {i}",
            "image": "https://placehold.co/600x400",
            "topic": first_topic
        }
        for i in range(1, 10)
    ]
    
    if not Post.objects.exists():
        Post.objects.bulk_create([Post(**data) for data in post_data])

def clearPosts():
    '''
    Временная функция для очистки базы от данных
    '''
    Post.objects.all().delete()
    