from django import forms
from .models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(UserCreationForm): 
    birthday = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label=_("Birthday")
    )

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "birthday", "avatar")


    
class UserLoginForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"))

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password", "is_active", "is_staff")

    def clean_password(self):
        return self.initial["password"]