from django.urls import path

from forum import views

# Называй методы контроллера как угодно, я их пишу чтоб бы пусто не было
urlpatterns = [
    path('', views.ForumIndexView.as_view(), name='index'),
    path('seed-data/', views.seedData, name='seed_data'),
    path('clear-data/', views.clearData, name='clear_data'),
    path('communities/', views.CategoryListView.as_view(), name='communities_list'),
    path('communities/create/', views.CategoryCreateView.as_view(), name='community_create'),
    path('communities/<int:category_id>/<slug:slug>/', views.CategoryDetailView.as_view(), name='community_detail'),
    path('communities/<int:category_id>/<slug:slug>/update/', views.CategoryUpdateView.as_view(), name='community_update'),
    path('communities/<int:category_id>/<slug:slug>/delete/', views.CategoryDeleteView.as_view(), name='community_delete'),
    path('communities/<int:category_id>/<slug:slug>/create-topic/', views.TopicCreateView.as_view(), name='create_topic'),
    
    path('topic/<int:topic_id>/<slug:slug>/create-post/', views.PostCreateView.as_view(), name='create_post'),
    path('topic/<int:topic_id>/<slug:slug>/', views.TopicPostListView.as_view(), name='topic_detail'),
    path('post/<int:post_id>/like/', views.ToggleLikeView.as_view(), name='post_toggle_like'),
]
