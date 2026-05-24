from django.urls import path

from forum import views

# Называй методы контроллера как угодно, я их пишу чтоб бы пусто не было
urlpatterns = [
    path('topics/<int:topic_id>-<str:slug>', views.topic_detail, name='topic_detail'),
]
