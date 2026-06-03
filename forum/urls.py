from django.urls import path

from forum import views

urlpatterns = [
    # --- Базовые маршруты ---
    path("", views.ForumIndexView.as_view(), name="index"),
    path("seed-data/", views.seedData, name="seed_data"),
    path("clear-data/", views.clearData, name="clear_data"),
    path(
        "sidebar/communities/",
        views.user_sidebar_communities_view,
        name="user_sidebar_communities",
    ),
    
    # --- Community (Сообщества) ---
    path("communities/", views.CommunityListView.as_view(), name="communities_list"),
    path(
        "communities/create/",
        views.CommunityCreateView.as_view(),
        name="community_create",
    ),
    path(
        "communities/<int:community_id>/<slug:slug>/",
        views.CommunityDetailView.as_view(),
        name="community_detail",
    ),
    path(
        "communities/<int:community_id>/<slug:slug>/update/",
        views.CommunityUpdateView.as_view(),
        name="community_update",
    ),
    path(
        "communities/<int:community_id>/<slug:slug>/delete/",
        views.CommunityDeleteView.as_view(),
        name="community_delete",
    ),
    path(
        "communities/create-topic/",
        views.TopicCreateView.as_view(),
        name="create_topic",
    ),
    # --- Topic (Темы) ---
    path(
        "topic/<int:topic_id>/<slug:slug>/",
        views.TopicPostListView.as_view(),
        name="topic_detail",
    ),
    path(
        "topic/<int:topic_id>/<slug:slug>/create-post/",
        views.PostCreateView.as_view(),
        name="create_post",
    ),
    # path('topic/<int:topic_id>/<slug:slug>/update/', views.TopicUpdateView.as_view(), name='topic_update'),
    # path('topic/<int:topic_id>/<slug:slug>/delete/', views.TopicDeleteView.as_view(), name='topic_delete'),
    # --- Post (Сообщения / Комментарии) ---
    path(
        "post/<int:post_id>/like/",
        views.ToggleLikeView.as_view(),
        name="post_toggle_like",
    ),
    # Новые маршруты для управления постами (будут обрабатывать AJAX-запросы):
    # path('post/<int:post_id>/update/', views.PostUpdateAjaxView.as_view(), name='post_update'),
    path(
        "post/<int:post_id>/delete/",
        views.PostDeleteAjaxView.as_view(),
        name="post_delete",
    ),
    path("post/<int:pk>/reply/", views.AddReplyView.as_view(), name="add_reply"),
    path(
        "communities/<int:community_id>/<slug:slug>/subscribe/",
        views.subscribe_to_community,
        name="subscribe_to_community",
    ),
]
