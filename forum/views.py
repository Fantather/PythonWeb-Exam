from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from forum.mixins import ViewTrackerMixin
from .managers import *
from forum.forms import CommunityForm, TopicCreateForm
from .models import Community, Topic, Post
from .helpers import seedDataHelper, clearDataHelper
from .services import CommunityService, PostService, TopicService, User

from django.db.models import Count
###temp

def seedData(request):
    """Представление для заполнения базы данных по запросу"""
    seedDataHelper(request)
    return HttpResponseRedirect(reverse("index"))


def clearData(request):
    clearDataHelper(request)
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
        context["community"] = Community.get_root_nodes().order_by("title")
        return context
    
    def get_queryset(self):
        #леша это не шарп, тут нет еще запроса. ListView видит paginate_by = 5 и будет кастрировать запрос
        return Topic.objects.all().select_related("community", "author").order_by("-is_pinned", "-last_active")


###############################Community Views ##############################
##crud
class CommunityListView(ListView):
    '''
    отображение всех сообществ
    '''
    model = Community
    template_name = "community_list.html"
    context_object_name = "community"
    paginate_by = 5
    search_fields = ["title", "slug"]

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            subscribers_count=Count("subscribers", distinct=True),
            topics_count=Count("topics__posts", distinct=True)
        )
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset.order_by("-subscribers_count", "-topics_count", "title")


class CommunityCreateView(LoginRequiredMixin, LoginRequiredMixin, CreateView):
    model = Community
    form_class = CommunityForm
    template_name = "community_form.html"
    success_url = reverse_lazy("communities_list")

    def form_valid(self, form):
        data = form.cleaned_data
        data['owner'] = self.request.user #Передаю автора в объект

        # Делегируем создание бизнес-логике сервиса
        self.object = CommunityService.create_root_community(
            title=data.get("title"),
            description=data.get("description", ""),
            icon=data.get("icon"),
            owner=self.request.user,
        )

        return redirect(self.get_success_url())


class CommunityUpdateView(UpdateView):
    '''
    редактирование сообщества
    '''
    model = Community
    form_class = CommunityForm
    template_name = "community_form.html"
    fields = ["title", "description"]
    login_required = True

    def get_success_url(self):
        return reverse_lazy("communities_list")

class CommunityDeleteView(DeleteView):
    '''
    удаление сообщества. С страницы пользователя что ей владеет
    '''
    model = Community
    success_url = reverse_lazy("communities_list")
    login_required = True

class CommunityDetailView(DetailView):
    '''
    отображение сообщества и всех его топиков
    '''
    model = Community
    template_name = "community_detail.html"
    context_object_name = "community"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        community = self.get_object()
        context["topics"] = Topic.objects.filter(community=community).order_by("-is_pinned", "-last_active")
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

class TopicCreateView(FormView):
    '''
    создание нового топика в сообществе
    FormView из за сервиса Леши
    '''
    model = Topic
    form_class = TopicCreateForm
    template_name = "topic_form.html"
    login_required = True

    def get_initial(self):
        initial = super().get_initial()
        community_id = self.kwargs.get("community_id")
        if community_id:
            initial["community"] = get_object_or_404(Community, pk=community_id)
        return initial
    
    def get_form(self, **kwargs):
        '''ограничение только тех сообществ что подписаны пользователю'''
        form = super().get_form(**kwargs)
        user_communities = Community.objects.filter(subscribers=self.request.user)
        form.fields["community"].queryset = user_communities

        return form

    def form_valid(self, form):
        title = form.cleaned_data['title']
        content = form.cleaned_data['content']
        community = form.cleaned_data['community']
        images = self.request.FILES.getlist('images')

        topic = TopicService.create_topic_with_post(
            community=community,
            author=self.request.user,
            title=title,
            content=content,
            images=images
        )
        return redirect(topic.get_absolute_url())


###############################Post Views ##############################
class PostCreateView(LoginRequiredMixin, CreateView):
    '''
    Создание нового поста (ответа) в топике
    '''
    model = Post
    template_name = "post_form.html"
    # Убрали 'image', так как его нет в модели. 
    # Оставили content и parent (если это ответ на другой комментарий)
    fields = ["content", "parent"] 

    def form_valid(self, form):
        topic_id = self.kwargs.get('topic_id')
        topic = get_object_or_404(Topic, pk=topic_id)
        images = self.request.FILES.getlist('images')
        
        self.object = PostService.create_reply(
            topic=topic,
            author=self.request.user,
            content=form.cleaned_data['content'],
            parent=form.cleaned_data.get('parent'), 
            images=images
        )
        
        return HttpResponseRedirect(topic.get_absolute_url())

class PostDeleteAjaxView(LoginRequiredMixin, View):
    """
    Удаление поста через AJAX-запрос.
    """
    def post(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, pk=post_id)
        
        # Серверная проверка прав
        if request.user != post.author:
            return JsonResponse({'status': 'error', 'message': 'Доступ запрещен'}, status=403)

        redirect_url = PostService.delete_post(post)
        
        # Если удалили корневой пост - получаем ссылку для перенаправления пользователя
        if redirect_url:
            return JsonResponse({
                'status': 'success', 
                'redirect_url': redirect_url
            })
            
        # Если это был обычный пост, то просто успех
        return JsonResponse({'status': 'success'})
    fields = ["content", "images"]
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

def subscribe_to_community(request, community_id):
    '''при нажатии на кнопку подписки, пользователь подписывается на сообщество и получает доступ к его топикам'''
    community = get_object_or_404(Community, pk=community_id)
    if request.user in community.subscribers.all():
        community.subscribers.remove(request.user)
    else:
        community.subscribers.add(request.user)
    return redirect(community.get_absolute_url())
