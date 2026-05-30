from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from forum.mixins import ViewTrackerMixin
from .managers import *
from forum.forms import CategoryForm
from .models import Community, Topic, Post
from .helpers import *
from .services import PostService

###temp

def seedData(request):
    """Представление для заполнения базы данных по запросу"""
    seedCategories()
    seedTopics()

    return HttpResponseRedirect(reverse("index"))


def clearData(request):
    clearCategories()
    clearTopics()
    
    return HttpResponseRedirect(reverse("index"))


# Create your views here.

class ForumIndexView(ListView):
    '''
    отображение категорий в виде карусели и список топиков
    '''
    model = Topic
    template_name = "index.html"
    context_object_name = "topics"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Community.get_root_nodes().order_by("title")
        return context
    
    def get_queryset(self):
        #леша это не шарп, тут нет еще запроса. ListView видит paginate_by = 5 и будет кастрировать запрос
        return Topic.objects.all().select_related("community", "author").order_by("-is_pinned", "-last_active")


###############################Category Views ##############################
##crud
class CategoryListView(ListView):
    '''
    отображение всех сообществ
    '''
    model = Community
    template_name = "community_list.html"
    context_object_name = "categories"
    paginate_by = 5
    search_fields = ["title", "slug"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset.order_by("title")
    

class CategoryCreateView(CreateView):
    '''
    создание нового сообщества
        '''
    model = Community
    form_class = CategoryForm
    template_name = "community_form.html"
    success_url = reverse_lazy("communities_list")
    login_required = True

    def form_valid(self, form):
        parent_id = self.request.GET.get("parent")
        
        data = form.cleaned_data
        
        if parent_id:
            parent_category = Community.objects.get(id=parent_id)
            self.object = parent_category.add_child(**data)
        else:
            # Создаем независимую корневую категорию
            self.object = Community.add_root(**data)
            
        return HttpResponseRedirect(self.get_success_url())
    
class CategoryUpdateView(UpdateView):
    '''
    редактирование сообщества
    '''
    model = Community
    form_class = CategoryForm
    template_name = "community_form.html"
    fields = ["title", "description"]
    login_required = True

    def get_success_url(self):
        return reverse_lazy("communities_list")

class CategoryDeleteView(DeleteView):
    '''
    удаление сообщества. С страницы пользователя что ей владеет
    '''
    model = Community
    success_url = reverse_lazy("communities_list")
    login_required = True

class CategoryDetailView(DetailView):
    '''
    отображение категории и всех ее топиков
    '''
    model = Community
    template_name = "community_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context["topics"] = Topic.objects.filter(category=category).order_by("-is_pinned", "-last_active")
        return context


##############################Topic Views ##############################
class TopicListView(ListView):
    '''
    отображение всех топиков в сообществе
    топик это тема, которая может содержать в себе посты (сообщения)
    они отсортированы по дате последней активности (создание или обновление поста)
    и по флагу is_pinned, который указывает, закреплен ли топик

    '''
    model = Topic
    template_name = "topic_list.html"
    context_object_name = "topics"

    def get_queryset(self):
        categories_id = self.kwargs.get("categories_id")
        return Topic.objects.filter(category_id=categories_id).order_by("-is_pinned", "-last_active")
    
class TopicDetailView(DetailView):
    '''
    отображение топика и всех его постов
    '''
    model = Topic
    template_name = "topic_detail.html"
    context_object_name = "topic"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.get_object()
        context["posts"] = Post.objects.filter(topic=topic).order_by("created_at")
        return context
    
class TopicCreateView(CreateView):
    '''
    создание нового топика в сообществе
    '''
    model = Topic
    template_name = "topic_form.html"
    fields = ["title"]
    login_required = True

###############################Post Views ##############################
class PostCreateView(CreateView):
    '''
    создание нового поста в топике
    '''
    model = Post
    template_name = "post_form.html"
    fields = ["content", "image"]
    login_required = True


class TopicPostListView(ViewTrackerMixin, ListView):
    """
    Контроллер для вывода дерева обсуждения (постов) в конкретном топике.
    Ожидает 'topic_id' в параметрах URL.
    """
    model = Post
    template_name = "forum/topic_posts.html"
    context_object_name = "flat_posts"
    paginate_by = 20

    # --- Настройки для ViewTrackerMixin ---
    view_tracker_model = Topic
    view_tracker_kwarg = 'topic_id'


    def get_queryset(self):
        """
        Извлекает посты, относящиеся к топику, с агрессивной загрузкой авторов.
        """
        self.topic_id = self.kwargs.get("topic_id")
        return Post.objects.thread(self.topic_id)

    def get_context_data(self, **kwargs):
        """
        Добавляет объект Topic в контекст. 
        """
        context = super().get_context_data(**kwargs)

        posts = list(context["flat_posts"])
        post_dict = {post.id: post for post in posts}   # Словарь для быстрого поиска постов по ID (O(1))
        root_posts = []

        #Инициализируем пустой список детей для каждого поста, это нужно делать тут, что бы хранилища оставались независимыми
        for post in posts:
            post.children = []

        for post in posts:
            if post.parent_id:
                post_dict[post.parent_id].children.append(post)
            elif not post.parent_id:
                root_posts.append(post)

            context["nested_posts"] = root_posts
            context["topic"] = get_object_or_404(
                Topic.objects.select_related('community'),
                pk = self.topic_id
            )

        return context
    
class ToggleLikeView(LoginRequiredMixin, View):
    def handle_no_permission(self):
        """
        Переопределяем поведение для неавторизованных пользователей.
        Вместо редиректа на страницу логина, отдаем ошибку 401 в формате JSON.
        """
        return JsonResponse({
            'status': 'error', 
            'message': 'Требуется авторизация'
        }, status=401)
    
    def post(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, pk=post_id)
        is_liked = PostService.toggle_like(post, request.user)

        post.refresh_from_db(fields=['likes_count'])
        return JsonResponse({
            'status': 'success',
            'is_liked': is_liked,
            'likes_count': post.likes_count
        })
