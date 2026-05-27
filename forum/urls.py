from django.urls import path

from forum import views

# Называй методы контроллера как угодно, я их пишу чтоб бы пусто не было
urlpatterns = [
    path('', views.ForumIndexView.as_view(), name='index'),
    path('seed-data/', views.seedData, name='seed_data'),
    path('clear-data/', views.clearData, name='clear_data'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    
    path('topic/<int:topic_id>/<slug:slug>/', views.TopicPostListView.as_view(), name='topic_detail')
]
