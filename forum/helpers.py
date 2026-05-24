from .models import Category, Topic, Post

def seedCategories():
    '''
    Временная функция для заполнения базы данными
    '''
    categ_data = [
        {
            "title": f"Категория {i}",
            "description": f"Описание категории {i}",
            # Убедитесь, что передача URL строкой не вызовет отдельную 
            # ошибку валидации FileField при сохранении.
        }
        for i in range(1, 10)
    ]   
    
    if not Category.objects.exists():
        # Используем add_root вместо bulk_create для корректной генерации полей MP_Node
        for data in categ_data:
            Category.add_root(**data)

            
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

    pass

def clearPosts():
    '''
    Временная функция для очистки базы от данных
    '''
    Post.objects.all().delete()
