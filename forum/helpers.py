from django.http import HttpResponse
from django.core.management import call_command

def seedDataHelper(request):
    """
    Вызывает вашу консольную команду seed_forum прямо из браузера.
    """
    try:
        # Имя 'seed_forum' должно совпадать с названием файла в папке management/commands
        call_command('seed_forum')
        return HttpResponse("Сидирование базы данных успешно завершено! Проверьте главную страницу.")
    except Exception as e:
        return HttpResponse(f"Произошла ошибка при сидировании: {str(e)}", status=500)

def clearDataHelper(request):
    """
    Если у вас есть команда для очистки (например, clear_forum), 
    её можно вызвать точно так же.
    """
    # Временно оставим прямое удаление, если команды пока нет
    from forum.models import Community, Topic, Post
    Post.objects.all().delete()
    Topic.objects.all().delete()
    Community.objects.all().delete()
    return HttpResponse("База данных очищена.")
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
