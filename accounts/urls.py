from django.urls import path

from . import views

# Называй методы контроллера как угодно, я их пишу чтоб бы пусто не было
urlpatterns = [
    path('register/', views.RegisterPageView.as_view(), name='register'),
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/<str:username>/', views.UserPageView.as_view(), name='user_page'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit_profile'),
]
