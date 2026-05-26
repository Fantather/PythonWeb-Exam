from django import forms


from forum.models import Category, Topic
from core.models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        strip=False,
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput,
        strip=False
    )

    
    birthday = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label=_("Birthday")
    )

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password1","password2", "birthday", "avatar")

        
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))
    
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        
        return user
    
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
    


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["title", "description", "icon"]

        widgets = {
        'title': forms.TextInput(attrs={'class': 'validate'}),
        'description': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        'icon': forms.ClearableFileInput(attrs={'class': 'file-input'}),
        }



#вдруг сортировка понадобится, вот у меня пример из дз будет, просто перепишу под что надо
# class FilmFilterForm(forms.Form):
#     sort_choices = [
#         ('title', 'По названию'),
#         ('-title', 'По названию (убывание)'),
#         ('-release_year', 'Год выхода'),
#         ('release_year', 'Год выхода (возрастание)'),
#         ('-rating', 'Рейтинг (убывание)'),
#         ('rating', 'Рейтинг (возрастание)'),

#     ]
#     sort = forms.ChoiceField(
#         choices=sort_choices, 
#         required=False, 
#         initial='title',
#         widget=forms.Select(attrs={'id': 'sort-select'})
#         )

