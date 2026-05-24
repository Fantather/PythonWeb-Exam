from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Category, Topic, Post
from .helpers import *
###temp

# seedCategories()
# seedTopics()

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
        context["categories"] = Category.get_root_nodes().order_by("title")
        return context
    
    def get_queryset(self):
        #леша это не шарп, тут нет еще запроса. ListView видит paginate_by = 5 и будет кастрировать запрос
        return Topic.objects.all().select_related("category").order_by("-is_pinned", "-last_active")


###############################Category Views ##############################
##crud
class CategoryListView(ListView):
    '''
    отображение всех категорий на главной странице форума
    '''
    model = Category
    template_name = "forum/category_list.html"
    context_object_name = "categories"

class CategoryCreateView(CreateView):
    '''
    создание новой категории
    '''
    model = Category
    template_name = "forum/category_form.html"
    fields = ["title", "description"]

class CategoryUpdateView(UpdateView):
    '''
    редактирование категории
    '''
    model = Category
    template_name = "category_form.html"
    fields = ["title", "description"]

class CategoryDeleteView(DeleteView):
    '''
    удаление категории
    '''
    model = Category
    template_name = "category_confirm_delete.html"
    success_url = "/"

##############################Topic Views ##############################
class TopicListView(ListView):
    '''
    отображение всех топиков в категории
    топик это тема, которая может содержать в себе посты (сообщения)
    они отсортированы по дате последней активности (создание или обновление поста)
    и по флагу is_pinned, который указывает, закреплен ли топик

    '''
    model = Topic
    template_name = "topic_list.html"
    context_object_name = "topics"

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        return Topic.objects.filter(category_id=category_id).order_by("-is_pinned", "-last_active")
    
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
    
###############################Post Views ##############################
class PostCreateView(CreateView):
    '''
    создание нового поста в топике
    '''
    model = Post
    template_name = "post_form.html"
    fields = ["content", "image"]




