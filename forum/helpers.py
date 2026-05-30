from django.contrib.auth import get_user_model
from .models import Community, Topic, Post

def clearCategories():
    '''
    Временная функция для очистки базы от данных
    '''
    Community.objects.all().delete()
    
def clearTopics():
    '''
    Временная функция для очистки базы от данных
    '''
    Topic.objects.all().delete()

def clearPosts():
    '''
    Временная функция для очистки базы от данных
    '''
    Post.objects.all().delete()