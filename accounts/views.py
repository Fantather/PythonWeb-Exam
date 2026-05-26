from urllib import request

from django.shortcuts import render

# Create your views here.

from django.http import HttpRequest, HttpResponse
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from accounts.forms import UserRegistrationForm, UserLoginForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView

from accounts.models import User



class RegisterPageView(CreateView):
    template_name = "register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        
        return response
    

class LoginPageView(LoginView):
    template_name = "login.html" 
    redirect_authenticated_user = True 

    def get_success_url(self):
        return reverse_lazy("user_page", kwargs={"username": self.request.user.username})


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("login")

class UserPageView(DetailView):
    model = User
    template_name = "user_page.html"
    context_object_name = "user"

    slug_field = "username" 
    slug_url_kwarg = "username"

    login_required = True
    

class EditProfileView(UpdateView):
    model = User
    template_name = "edit_profile.html"
    form_class = UserChangeForm
    success_url = reverse_lazy("user_page")

    def get_object(self, queryset=None):
        return self.request.user
    
    # def get_success_url(self):
    #  return reverse_lazy("user_page", kwargs={"username": self.request.user.username})

